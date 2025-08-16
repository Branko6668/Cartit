from rest_framework.views import APIView
from apps.shopping_cart.models import ShoppingCart
from apps.shopping_cart.serializers import ShoppingCartSerializer
from utils.renderer import CustomResponse


class ShoppingCartAPIView(APIView):
    # @todo: 登录权限验证
    """
    购物车 API 视图
    访问方式：shopping_cart/
    处理 GET 和 POST 请求
    """
    def get(self, request):
        # 获取购物车信息
        user_id = request.query_params.get("user_id")
        if user_id is None:
            return CustomResponse(code=3400, msg="缺少参数: user_id", errors={"user_id": "required"}, status=400)
        try:
            uid = int(user_id)
        except (TypeError, ValueError):
            return CustomResponse(code=3400, msg="参数格式错误: user_id 应为整数", errors={"user_id": "invalid"}, status=400)

        shopping_cart_items = ShoppingCart.objects.filter(user_id=uid)
        shopping_cart_serialize = ShoppingCartSerializer(shopping_cart_items, many=True)
        return CustomResponse(code=3000, msg='获取购物车信息成功', data=shopping_cart_serialize.data, status=200)

    def post(self, request):
        # 添加商品到购物车 / 更新数量 / 数量为 0 则删除
        request_data = request.data or {}
        missing = [k for k in ("user_id", "product_id", "quantity") if k not in request_data]
        if missing:
            return CustomResponse(code=3400, msg="缺少必要参数", errors={k: "required" for k in missing}, status=400)
        try:
            user_id = int(request_data["user_id"])
            product_id = int(request_data["product_id"])
            quantity = int(request_data["quantity"])
        except (TypeError, ValueError):
            return CustomResponse(code=3400, msg="参数格式错误: user_id/product_id/quantity 应为整数", errors={"user_id": "int", "product_id": "int", "quantity": "int"}, status=400)

        if quantity == 0:
            return CustomResponse(code=4000, msg='无效更新操作', data=None, status=400)

        # 判断数据是否存在，否则就创建新的购物车项
        data_exists = ShoppingCart.objects.filter(user_id=user_id, product_id=product_id)
        if data_exists.exists():
            # 如果购物车项已存在，则更新数量
            shopping_cart_item = data_exists.first()
            shopping_cart_item.quantity += quantity
            if shopping_cart_item.quantity == 0:
                shopping_cart_item.delete()
                return CustomResponse(code=3002, msg='商品已从购物车移除', data=None, status=200)
            elif shopping_cart_item.quantity < 0:
                return CustomResponse(code=4000, msg='商品数量不能小于0', data=None, status=400)
            else:
                shopping_cart_item.save()
                shopping_cart_serialize = ShoppingCartSerializer(shopping_cart_item)
                return CustomResponse(code=3001, msg='更新购物车成功', data=shopping_cart_serialize.data, status=200)
        else:
            # 创建新的购物车项
            shopping_cart_item = ShoppingCart.objects.create(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            shopping_cart_serialize = ShoppingCartSerializer(shopping_cart_item)
            return CustomResponse(code=3001, msg='添加购物车成功', data=shopping_cart_serialize.data, status=201)
