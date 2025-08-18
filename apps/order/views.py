from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from apps.order.models import OrderInfo
from apps.order.serializers import OrderInfoSerializer
from utils.renderer import CustomResponse
from .services import create_orders_from_cart, create_order_direct


class OrderCreateAPIView(APIView):
    permission_classes = []

    def post(self, request: Request):
        data = request.data or {}
        required_fields = ["recipient"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return CustomResponse(code=3400, msg="缺少必要参数", errors={f: "required" for f in missing}, status=HTTP_400_BAD_REQUEST)

        recipient = data.get("recipient", {})
        for field in ["name", "phone", "address"]:
            if field not in recipient or not recipient[field]:
                return CustomResponse(code=3400, msg=f"收件人信息缺失: {field}", errors={field: "required"}, status=HTTP_400_BAD_REQUEST)

        remark = data.get("remark", "")
        user_id = 15  # ✅ 开发阶段写死

        try:
            orders = create_orders_from_cart(user_id=user_id, recipient=recipient, remark=remark)
        except ValueError as e:
            return CustomResponse(code=3401, msg="订单创建失败", errors={"detail": str(e)}, status=HTTP_400_BAD_REQUEST)

        serialized = [OrderInfoSerializer(o).data for o in orders]
        return CustomResponse(code=3000, msg="订单创建成功", data=serialized, status=HTTP_201_CREATED)


class DirectOrderCreateAPIView(APIView):
    permission_classes = []

    def post(self, request: Request):
        data = request.data or {}
        required_fields = ["product_id", "quantity", "recipient"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return CustomResponse(code=3400, msg="缺少必要参数", errors={f: "required" for f in missing}, status=HTTP_400_BAD_REQUEST)

        try:
            product_id = int(data["product_id"])
            quantity = int(data["quantity"])
        except (TypeError, ValueError):
            return CustomResponse(code=3400, msg="参数格式错误", errors={"product_id": "int", "quantity": "int"}, status=HTTP_400_BAD_REQUEST)

        recipient = data["recipient"]
        for field in ["name", "phone", "address"]:
            if field not in recipient or not recipient[field]:
                return CustomResponse(code=3400, msg=f"收件人信息缺失: {field}", errors={field: "required"}, status=HTTP_400_BAD_REQUEST)

        remark = data.get("remark", "")
        user_id = 15  # 开发阶段写死

        try:
            order = create_order_direct(user_id=user_id, product_id=product_id, quantity=quantity, recipient=recipient, remark=remark)
        except ValueError as e:
            return CustomResponse(code=3401, msg="订单创建失败", errors={"detail": str(e)}, status=HTTP_400_BAD_REQUEST)

        serialized = OrderInfoSerializer(order)
        return CustomResponse(code=3000, msg="订单创建成功", data=serialized.data, status=HTTP_201_CREATED)