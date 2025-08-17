from django.core.paginator import Paginator
from rest_framework.views import APIView
from apps.product.models import Category
from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from utils.renderer import CustomResponse
from rest_framework.generics import ListAPIView


class ProductMainMenuView(APIView):
    """
    商品主菜单视图
    访问方式：product/main_menu/
    仅处理 GET 请求
    """
    @staticmethod
    def get(request):
        # 顶级分类（parent_id=0）
        main_menus = Category.objects.filter(parent_id=0)
        result_list = [m.to_menu_item() for m in main_menus]
        return CustomResponse(code=1000, msg="获取主菜单成功", data=result_list, status=200)


class ProductSubMenuView(APIView):
    """
    商品子菜单视图
    访问方式：product/sub_menu/
    仅处理 GET 请求
    """
    @staticmethod
    def get(request):
        main_menu_id = request.query_params.get("main_menu_id")
        if main_menu_id is None:
            return CustomResponse(code=1400, msg="缺少参数: main_menu_id", errors={"main_menu_id": "required"}, status=400)
        try:
            pid = int(main_menu_id)
        except (TypeError, ValueError):
            return CustomResponse(code=1400, msg="参数格式错误: main_menu_id 应为整数", errors={"main_menu_id": "invalid"}, status=400)

        sub_menus = Category.objects.filter(parent_id=pid)
        result_list = [m.to_menu_item() for m in sub_menus]
        return CustomResponse(code=1001, msg="获取子菜单成功", data=result_list, status=200)


class ProductSubSubMenuView(APIView):
    """
    商品子子菜单视图
    访问方式：product/sub_sub_menu/
    仅处理 GET 请求
    """
    @staticmethod
    def get(request):
        sub_menu_id = request.query_params.get("sub_menu_id")
        if sub_menu_id is None:
            return CustomResponse(code=1400, msg="缺少参数: sub_menu_id", errors={"sub_menu_id": "required"}, status=400)
        try:
            pid = int(sub_menu_id)
        except (TypeError, ValueError):
            return CustomResponse(code=1400, msg="参数格式错误: sub_menu_id 应为整数", errors={"sub_menu_id": "invalid"}, status=400)

        sub_sub_menus = Category.objects.filter(parent_id=pid)
        result_list = [m.to_menu_item() for m in sub_sub_menus]
        return CustomResponse(code=1002, msg="获取子子菜单成功", data=result_list, status=200)


class ProductTagAPIView(ListAPIView):
    """
    商品标签 API 视图
    路由：product/tags/<int:product_tag_id>/<int:page>/
    仅处理 GET 请求
    """
    serializer_class = ProductSerializer
    def list(self, request, *args, **kwargs):
        try:
            page = int(kwargs.get("page"))
            tag_id = int(kwargs.get("product_tag_id"))
        except (TypeError, ValueError):
            return CustomResponse(
                code=2400,
                msg="参数错误，page与product_tag_id应为整数",
                errors={"product_tag_id": "invalid", "page": "invalid"},
                status=400
            )
        if page <= 0:
            return CustomResponse(
                code=2400,
                msg="page不能小于等于0",
                errors={"page": "invalid"},
                status=400
            )
        queryset = Product.objects.filter(tags__id=tag_id)
        paginator = Paginator(queryset, 20)
        try:
            page = paginator.get_page(page)
        except Exception:
            return CustomResponse(
                code=2400,
                msg="页面超出范围",
                errors={"page": "out of range"},
                status=404
            )
        page_serialize = self.get_serializer(page.object_list, many=True)
        return CustomResponse(
            code=2000,
            msg="",
            data=page_serialize.data,
            status=200
        )

class ProductQueryAPIView(APIView):
    """
    商品详情查询 API 视图
    路由：product/query/<int:id>/
    仅处理 GET 请求
    """
    def get(self, request, id):
        try:
            product_id = int(id)
        except (TypeError, ValueError):
            return CustomResponse(code=2400, msg="参数格式错误: id 应为整数", errors={"id": "invalid"}, status=400)

        try:
            product_data = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return CustomResponse(code=2400, msg="商品不存在", errors={"id": product_id}, status=404)

        result = ProductSerializer(instance=product_data).data
        return CustomResponse(code=2001, msg="获取商品详情成功", data=result, status=200)
