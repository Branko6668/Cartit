"""
Shopping Cart 模块视图（扩展版）

接口一览：
- GET    /shopping_cart/                     列表+汇总（基于 Token 用户）
- POST   /shopping_cart/                     添加 / 增量 / 设定数量  mode=add|set
- PATCH  /shopping_cart/item/<id>/           修改数量或选中状态
- DELETE /shopping_cart/item/<id>/           删除条目
- POST   /shopping_cart/select_all           全选 / 全不选 {selected:bool}
- POST   /shopping_cart/clear                清空购物车 {only_selected:bool}

注意：
1. 已移除对 user_id 查询参数的依赖；若前端仍传，后端忽略，以 Token 解析为准。
2. 认证：使用自定义 JWT 方案，在 request.auth 中读取 payload['user_id']；未携带 Token 返回 4101。
3. 错误码：
   - 3000 列表成功
   - 3001 增量添加 / 更新成功
   - 3003 设定数量成功
   - 3002 条目被移除
   - 3004 清空成功
   - 3400 参数错误
   - 3402 库存不足
   - 3404 商品已下架
   - 4101 未登录
"""

from typing import Dict, Any, List
from django.db import transaction
from django.db.models import F, QuerySet
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from django.shortcuts import get_object_or_404
from utils.renderer import CustomResponse
from utils.error_codes import Codes
from apps.shopping_cart.models import ShoppingCart
from apps.shopping_cart.serializers import ShoppingCartSerializer
from apps.product.models import Product


# ====================== 工具函数 ======================

def _unauthorized():
    return CustomResponse(code=Codes.UNAUTHORIZED, msg="未登录", status=401)


def _get_user_id(request: Request):
    payload = getattr(request, 'auth', None)
    if not payload or not isinstance(payload, dict) or 'user_id' not in payload:
        return None
    return payload['user_id']


def _build_summary(qs: QuerySet) -> Dict[str, Any]:
    total_count = qs.count()
    items = list(qs)
    selected_items = [i for i in items if i.selected]

    def price(p: Product):
        return p.price

    selected_amount = sum(price(i.product) * i.quantity for i in selected_items)
    total_amount = sum(price(i.product) * i.quantity for i in items)
    # 按店铺分组（仅选中项）
    per_store: Dict[int, Dict[str, Any]] = {}
    for i in selected_items:
        sid = i.product.store_id
        if sid not in per_store:
            per_store[sid] = {
                'store_id': sid,
                'store_name': getattr(i.product.store, 'store_name', None),
                'selected_subtotal': 0
            }
        per_store[sid]['selected_subtotal'] += price(i.product) * i.quantity
    # 转换格式与字符串化金额
    def m(val):
        return str(val)
    stores = [
        {
            'store_id': v['store_id'],
            'store_name': v['store_name'],
            'selected_subtotal': m(v['selected_subtotal'])
        } for v in per_store.values()
    ]
    return {
        'total_count': total_count,
        'selected_count': len(selected_items),
        'total_amount': m(total_amount),
        'selected_amount': m(selected_amount),
        'discount_amount': '0.00',  # 预留
        'payable_amount': m(selected_amount),
        'stores': stores
    }


# ====================== 视图 ======================

class ShoppingCartListCreateAPIView(APIView):
    """GET 列表 + 汇总；POST 添加/设定数量。"""

    def get(self, request: Request):
        user_id = _get_user_id(request)
        if not user_id:
            return _unauthorized()
        qs = ShoppingCart.objects.filter(user_id=user_id).select_related('product', 'product__store')
        serializer = ShoppingCartSerializer(qs, many=True)
        summary = _build_summary(qs)
        return CustomResponse(code=Codes.CART_LIST_OK, msg='获取购物车成功', data={'items': serializer.data, 'summary': summary}, status=200)

    @transaction.atomic
    def post(self, request: Request):
        user_id = _get_user_id(request)
        if not user_id:
            return _unauthorized()
        data = request.data or {}
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        mode = (data.get('mode') or 'add').lower()
        if product_id is None or quantity is None:
            return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg='缺少参数', errors={'product_id': 'required', 'quantity': 'required'}, status=400)
        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg='参数格式错误', errors={'product_id': 'int', 'quantity': 'int'}, status=400)
        if mode not in ('add', 'set'):
            return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg='mode 仅支持 add/set', errors={'mode': 'invalid'}, status=400)
        if quantity <= 0:
            return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg='数量必须大于0', errors={'quantity': 'gt0'}, status=400)
        # 获取商品
        try:
            product = Product.objects.select_related('store').get(id=product_id)
        except Product.DoesNotExist:
            return CustomResponse(code=Codes.PRODUCT_NOT_FOUND_OR_PARAM_ERROR, msg='商品不存在', status=404)
        if product.status in ('off_sale', 'out_of_stock'):
            return CustomResponse(code=Codes.PRODUCT_OFF_SHELF, msg='商品已下架或缺货', status=400)
        if product.stock < quantity and mode == 'set':
            return CustomResponse(code=Codes.STOCK_NOT_ENOUGH, msg='库存不足', errors={'stock': product.stock}, status=400)

        qs = ShoppingCart.objects.select_for_update().filter(user_id=user_id, product_id=product_id)
        created = False
        if qs.exists():
            cart_item = qs.first()
            if mode == 'add':
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product.stock:
                    return CustomResponse(code=Codes.STOCK_NOT_ENOUGH, msg='库存不足', errors={'stock': product.stock}, status=400)
                cart_item.quantity = new_quantity
                cart_item.selected = True  # 加入视为选中
                cart_item.save(update_fields=['quantity', 'selected', 'update_time'])
                code = Codes.CART_ADD_OR_UPDATE_OK
                msg = '更新购物车成功'
            else:  # set
                if quantity > product.stock:
                    return CustomResponse(code=Codes.STOCK_NOT_ENOUGH, msg='库存不足', errors={'stock': product.stock}, status=400)
                cart_item.quantity = quantity
                cart_item.selected = True
                cart_item.save(update_fields=['quantity', 'selected', 'update_time'])
                code = Codes.CART_SET_OK
                msg = '设定数量成功'
        else:
            if quantity > product.stock:
                return CustomResponse(code=Codes.STOCK_NOT_ENOUGH, msg='库存不足', errors={'stock': product.stock}, status=400)
            cart_item = ShoppingCart.objects.create(user_id=user_id, product_id=product_id, quantity=quantity, selected=True)
            created = True
            code = Codes.CART_ADD_OR_UPDATE_OK
            msg = '添加购物车成功'

        serializer = ShoppingCartSerializer(cart_item)
        # 附带最新 summary（可减少前端再次拉取）
        user_qs = ShoppingCart.objects.filter(user_id=user_id).select_related('product', 'product__store')
        summary = _build_summary(user_qs)
        return CustomResponse(code=code, msg=msg, data={'item': serializer.data, 'summary': summary, 'created': created}, status=200)


class ShoppingCartItemAPIView(APIView):
    """单条购物车条目：PATCH 修改数量/选中，DELETE 删除。"""
    def patch(self, request: Request, pk: int):
        user_id = _get_user_id(request)
        if not user_id:
            return _unauthorized()
        data = request.data or {}
        quantity = data.get('quantity')
        selected = data.get('selected')
        if quantity is None and selected is None:
            return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg='至少提供 quantity 或 selected', status=400)
        cart_item = get_object_or_404(ShoppingCart.objects.select_related('product', 'product__store'), pk=pk, user_id=user_id)
        product = cart_item.product
        if quantity is not None:
            try:
                q = int(quantity)
            except (TypeError, ValueError):
                return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg='quantity 必须为整数', errors={'quantity': 'int'}, status=400)
            if q <= 0:
                return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg='数量必须大于0', errors={'quantity': 'gt0'}, status=400)
            if product.status in ('off_sale', 'out_of_stock'):
                return CustomResponse(code=Codes.PRODUCT_OFF_SHELF, msg='商品已下架或缺货', status=400)
            if q > product.stock:
                return CustomResponse(code=Codes.STOCK_NOT_ENOUGH, msg='库存不足', errors={'stock': product.stock}, status=400)
            cart_item.quantity = q
        if selected is not None:
            if not isinstance(selected, bool):
                return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg='selected 应为布尔', errors={'selected': 'bool'}, status=400)
            cart_item.selected = selected
        cart_item.save()
        serializer = ShoppingCartSerializer(cart_item)
        user_qs = ShoppingCart.objects.filter(user_id=user_id).select_related('product', 'product__store')
        summary = _build_summary(user_qs)
        # 返回数量设定成功 or 更新成功
        code = Codes.CART_SET_OK if quantity is not None else Codes.CART_ADD_OR_UPDATE_OK
        return CustomResponse(code=code, msg='更新条目成功', data={'item': serializer.data, 'summary': summary}, status=200)

    def delete(self, request: Request, pk: int):
        user_id = _get_user_id(request)
        if not user_id:
            return _unauthorized()
        cart_item = get_object_or_404(ShoppingCart, pk=pk, user_id=user_id)
        cart_item.delete()
        user_qs = ShoppingCart.objects.filter(user_id=user_id).select_related('product', 'product__store')
        summary = _build_summary(user_qs)
        return CustomResponse(code=Codes.CART_ITEM_REMOVED, msg='条目已删除', data={'summary': summary}, status=200)


class ShoppingCartSelectAllAPIView(APIView):
    """全选 / 取消全选 {selected: true|false}"""
    def post(self, request: Request):
        user_id = _get_user_id(request)
        if not user_id:
            return _unauthorized()
        selected = request.data.get('selected')
        if not isinstance(selected, bool):
            return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg='selected 必须为布尔', errors={'selected': 'bool'}, status=400)
        ShoppingCart.objects.filter(user_id=user_id).update(selected=selected)
        qs = ShoppingCart.objects.filter(user_id=user_id).select_related('product', 'product__store')
        serializer = ShoppingCartSerializer(qs, many=True)
        summary = _build_summary(qs)
        return CustomResponse(code=Codes.CART_ADD_OR_UPDATE_OK, msg='操作成功', data={'items': serializer.data, 'summary': summary}, status=200)


class ShoppingCartClearAPIView(APIView):
    """清空购物车 或 仅清空已选 {only_selected: bool}"""
    def post(self, request: Request):
        user_id = _get_user_id(request)
        if not user_id:
            return _unauthorized()
        only_selected = bool(request.data.get('only_selected', False))
        base_qs = ShoppingCart.objects.filter(user_id=user_id)
        if only_selected:
            base_qs = base_qs.filter(selected=True)
        deleted, _ = base_qs.delete()
        qs = ShoppingCart.objects.filter(user_id=user_id)
        summary = _build_summary(qs)
        return CustomResponse(code=Codes.CART_CLEARED, msg='购物车已清空' if not only_selected else '已清空选中项', data={'deleted': deleted, 'summary': summary}, status=200)
