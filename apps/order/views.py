"""
Order 模块视图

- 创建订单（购物车 / 直接购买）
- 新增：订单列表 & 订单详情
- 使用 JWT 载荷中的 user_id（不再写死）
- 统一错误码映射
"""
from typing import Any, Dict, List
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from apps.order.serializers import (
    OrderInfoSerializer,
    OrderInfoWithItemsSerializer,
    OrderItemSerializer,
)
from apps.order.models import OrderInfo, OrderItem
from utils.renderer import CustomResponse
from .services import create_orders_from_cart, create_order_direct
from utils.error_codes import Codes

# ================= 工具函数 =================

def _get_user_id(request: Request):
    payload = getattr(request, 'auth', None)
    if isinstance(payload, dict) and 'user_id' in payload:
        return payload['user_id']
    return None

def _unauthorized():
    return CustomResponse(code=Codes.UNAUTHORIZED, msg='未登录', status=401)

_ERROR_MAP = {
    '购物车为空': Codes.ORDER_EMPTY_CART,
    '库存不足': Codes.ORDER_STOCK_NOT_ENOUGH,
    '商品不存在': Codes.ORDER_PRODUCT_NOT_FOUND,
    '非法数量': Codes.CART_OR_ORDER_PARAM_ERROR,
    '商品已下架': Codes.PRODUCT_OFF_SHELF,
}

def _map_error(e: ValueError):
    msg = str(e)
    code = _ERROR_MAP.get(msg, Codes.ORDER_CREATE_FAILED)
    return code, msg

# ================= 创建相关 =================

class OrderCreateAPIView(APIView):
    """基于购物车创建订单（按店铺拆单）。"""

    permission_classes: List = []

    def post(self, request: Request):
        user_id = _get_user_id(request)
        if not user_id:
            return _unauthorized()
        data: Dict[str, Any] = request.data or {}
        recipient = data.get('recipient')
        if not isinstance(recipient, dict):
            return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg='缺少必要参数: recipient', errors={'recipient': 'required'}, status=HTTP_400_BAD_REQUEST)
        for field in ['name', 'phone', 'address']:
            if not recipient.get(field):
                return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg=f'收件人信息缺失: {field}', errors={field: 'required'}, status=HTTP_400_BAD_REQUEST)
        remark = data.get('remark', '')
        try:
            orders = create_orders_from_cart(user_id=user_id, recipient=recipient, remark=remark)
        except ValueError as e:
            code, msg = _map_error(e)
            return CustomResponse(code=code, msg=msg, errors={'detail': msg}, status=HTTP_400_BAD_REQUEST)
        # 预取明细
        order_ids = [o.id for o in orders]
        qs = OrderInfo.objects.filter(id__in=order_ids).prefetch_related('orderitem_set')
        serialized = OrderInfoWithItemsSerializer(qs, many=True).data
        return CustomResponse(code=Codes.ORDER_CREATE_OK_ALIAS, msg='订单创建成功', data=serialized, status=HTTP_201_CREATED)


class DirectOrderCreateAPIView(APIView):
    """直接购买下单。"""
    permission_classes: List = []

    def post(self, request: Request):
        user_id = _get_user_id(request)
        if not user_id:
            return _unauthorized()
        data: Dict[str, Any] = request.data or {}
        required_fields = ['product_id', 'quantity', 'recipient']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg='缺少必要参数', errors={f: 'required' for f in missing}, status=HTTP_400_BAD_REQUEST)
        # 解析数字
        try:
            product_id = int(data['product_id'])
            quantity = int(data['quantity'])
        except (TypeError, ValueError):
            return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg='参数格式错误', errors={'product_id': 'int', 'quantity': 'int'}, status=HTTP_400_BAD_REQUEST)
        recipient = data['recipient']
        for field in ['name', 'phone', 'address']:
            if not recipient.get(field):
                return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg=f'收件人信息缺失: {field}', errors={field: 'required'}, status=HTTP_400_BAD_REQUEST)
        remark = data.get('remark', '')
        try:
            order = create_order_direct(user_id=user_id, product_id=product_id, quantity=quantity, recipient=recipient, remark=remark)
        except ValueError as e:
            code, msg = _map_error(e)
            return CustomResponse(code=code, msg=msg, errors={'detail': msg}, status=HTTP_400_BAD_REQUEST)
        order = OrderInfo.objects.prefetch_related('orderitem_set').get(id=order.id)
        serialized = OrderInfoWithItemsSerializer(order).data
        return CustomResponse(code=Codes.ORDER_CREATE_OK_ALIAS, msg='订单创建成功', data=serialized, status=HTTP_201_CREATED)

# ================= 查询相关 =================

class OrderPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100

class OrderListAPIView(APIView):
    """订单列表（可按状态过滤）。"""
    def get(self, request: Request):
        user_id = _get_user_id(request)
        if not user_id:
            return _unauthorized()
        status_filter = request.query_params.get('status')
        qs = OrderInfo.objects.filter(user_id=user_id).order_by('-create_time')
        if status_filter:
            qs = qs.filter(status=status_filter)
        qs = qs.prefetch_related('orderitem_set')
        paginator = OrderPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = OrderInfoWithItemsSerializer(page, many=True)
        data = {
            'results': serializer.data,
            'count': qs.count(),
            'page': paginator.page.number if hasattr(paginator, 'page') else 1,
            'page_size': paginator.get_page_size(request),
        }
        return CustomResponse(code=Codes.SUCCESS, msg='获取订单列表成功', data=data, status=200)

class OrderDetailAPIView(APIView):
    """订单详情（含明细）。"""
    def get(self, request: Request, pk: int):
        user_id = _get_user_id(request)
        if not user_id:
            return _unauthorized()
        order = get_object_or_404(OrderInfo.objects.prefetch_related('orderitem_set'), pk=pk, user_id=user_id)
        serializer = OrderInfoWithItemsSerializer(order)
        return CustomResponse(code=Codes.SUCCESS, msg='获取订单详情成功', data=serializer.data, status=200)
