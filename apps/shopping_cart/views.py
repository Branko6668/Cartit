from rest_framework.response import Response
from rest_framework.views import APIView
from apps.shopping_cart.models import ShoppingCart
from apps.shopping_cart.serializers import ShoppingCartSerializer

class ShoppingCartAPIView(APIView):
    # @todo: 登录权限验证
    """
    购物车 API 视图
    访问方式：shopping_cart/
    处理 GET 和 POST 请求
    """
    def get(self, request):
        # 获取购物车信息
        pass

    def post(self, request):
        # 添加商品到购物车
        request_data = request.data
        user_id = int(request_data["user_id"])
        product_id = int(request_data["product_id"])
        quantity = int(request_data["quantity"])

        # 判断数据是否存在，否则就创建新的购物车项
        data_exists = ShoppingCart.objects.filter(user_id=user_id, product_id=product_id)
        if data_exists.exists():
            # 如果购物车项已存在，则更新数量
            shopping_cart_item = data_exists.first()
            shopping_cart_item.quantity += quantity
            shopping_cart_item.save()
            shopping_cart_serialize = ShoppingCartSerializer(shopping_cart_item)
            return Response(shopping_cart_serialize.data)
        else:
            # 创建新的购物车项
            shopping_cart_item = ShoppingCart.objects.create(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            shopping_cart_serialize = ShoppingCartSerializer(shopping_cart_item)
            return Response(shopping_cart_serialize.data)
