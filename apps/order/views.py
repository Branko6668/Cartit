"""
Order 模块视图

- 提供创建订单（基于购物车）与直接下单接口
- 使用 CustomResponse 统一响应结构
- 开发阶段 user_id 写死为 9，后续可替换为认证上下文
"""
from typing import Any, Dict
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from apps.order.serializers import OrderInfoSerializer
from utils.renderer import CustomResponse
from .services import create_orders_from_cart, create_order_direct
from utils.error_codes import Codes


class OrderCreateAPIView(APIView):
    """基于购物车创建订单。

    请求体：
      - recipient: {name, phone, address}
      - remark: 可选
    返回：创建出的订单列表
    """

    permission_classes = []

    def post(self, request: Request):
        data: Dict[str, Any] = request.data or {}
        required_fields = ["recipient"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg="缺少必要参数", errors={f: "required" for f in missing}, status=HTTP_400_BAD_REQUEST)

        recipient = data.get("recipient", {})
        for field in ["name", "phone", "address"]:
            if field not in recipient or not recipient[field]:
                return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg=f"收件人信息缺失: {field}", errors={field: "required"}, status=HTTP_400_BAD_REQUEST)

        remark = data.get("remark", "")
        user_id = 9  # ✅ 开发阶段写死，TODO: 从认证上下文获取

        try:
            orders = create_orders_from_cart(user_id=user_id, recipient=recipient, remark=remark)
        except ValueError as e:
            return CustomResponse(code=Codes.ORDER_CREATE_FAILED, msg="订单创建失败", errors={"detail": str(e)}, status=HTTP_400_BAD_REQUEST)

        serialized = [OrderInfoSerializer(o).data for o in orders]
        # 兼容现有前端仍返回 3000（Codes.CART_LIST_OK / ORDER_CREATE_OK_ALIAS）
        return CustomResponse(code=Codes.ORDER_CREATE_OK_ALIAS, msg="订单创建成功", data=serialized, status=HTTP_201_CREATED)


class DirectOrderCreateAPIView(APIView):
    """直接购买下单。

    请求体：
      - product_id: int
      - quantity: int
      - recipient: {name, phone, address}
      - remark: 可选
    返回：创建出的单个订单
    """

    permission_classes = []

    def post(self, request: Request):
        data: Dict[str, Any] = request.data or {}
        required_fields = ["product_id", "quantity", "recipient"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg="缺少必要参数", errors={f: "required" for f in missing}, status=HTTP_400_BAD_REQUEST)

        try:
            product_id = int(data["product_id"])
            quantity = int(data["quantity"])
        except (TypeError, ValueError):
            return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg="参数格式错误", errors={"product_id": "int", "quantity": "int"}, status=HTTP_400_BAD_REQUEST)

        recipient = data["recipient"]
        for field in ["name", "phone", "address"]:
            if field not in recipient or not recipient[field]:
                return CustomResponse(code=Codes.CART_OR_ORDER_PARAM_ERROR, msg=f"收件人信息缺失: {field}", errors={field: "required"}, status=HTTP_400_BAD_REQUEST)

        remark = data.get("remark", "")
        user_id = 9  # 开发阶段写死，TODO: 从认证上下文获取

        try:
            order = create_order_direct(user_id=user_id, product_id=product_id, quantity=quantity, recipient=recipient, remark=remark)
        except ValueError as e:
            return CustomResponse(code=Codes.ORDER_CREATE_FAILED, msg="订单创建失败", errors={"detail": str(e)}, status=HTTP_400_BAD_REQUEST)

        serialized = OrderInfoSerializer(order)
        return CustomResponse(code=Codes.ORDER_CREATE_OK_ALIAS, msg="订单创建成功", data=serialized.data, status=HTTP_201_CREATED)
