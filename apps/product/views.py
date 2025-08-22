"""
Product 模块视图

- 提供分类菜单与商品详情/标签列表接口
- 统一使用 CustomResponse 返回结构
"""

from typing import Any
from django.core.paginator import Paginator
from rest_framework.views import APIView
from apps.product.models import Category
from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from utils.renderer import CustomResponse
from rest_framework.generics import ListAPIView
from utils.error_codes import Codes


class ProductMainMenuView(APIView):
    """获取一级分类菜单（parent_id=0）。路由：/product/main_menu/"""

    @staticmethod
    def get(request):
        # 顶级分类（parent_id=0）
        main_menus = Category.objects.filter(parent_id=0)
        result_list = [m.to_menu_item() for m in main_menus]
        return CustomResponse(code=Codes.CATEGORY_MAIN_MENU_OK, msg="获取主菜单成功", data=result_list, status=200)


class ProductSubMenuView(APIView):
    """获取二级分类菜单。路由：/product/sub_menu/?main_menu_id=<int>"""

    @staticmethod
    def get(request):
        main_menu_id = request.query_params.get("main_menu_id")
        if main_menu_id is None:
            return CustomResponse(code=Codes.CATEGORY_PARAM_ERROR, msg="缺少参数: main_menu_id", errors={"main_menu_id": "required"}, status=400)
        try:
            pid = int(main_menu_id)
        except (TypeError, ValueError):
            return CustomResponse(code=Codes.CATEGORY_PARAM_ERROR, msg="参数格式错误: main_menu_id 应为整数", errors={"main_menu_id": "invalid"}, status=400)

        sub_menus = Category.objects.filter(parent_id=pid)
        result_list = [m.to_menu_item() for m in sub_menus]
        return CustomResponse(code=Codes.CATEGORY_SUB_MENU_OK, msg="获取子菜单成功", data=result_list, status=200)


class ProductSubSubMenuView(APIView):
    """获取三级分类菜单。路由：/product/sub_sub_menu/?sub_menu_id=<int>"""

    @staticmethod
    def get(request):
        sub_menu_id = request.query_params.get("sub_menu_id")
        if sub_menu_id is None:
            return CustomResponse(code=Codes.CATEGORY_PARAM_ERROR, msg="缺少参数: sub_menu_id", errors={"sub_menu_id": "required"}, status=400)
        try:
            pid = int(sub_menu_id)
        except (TypeError, ValueError):
            return CustomResponse(code=Codes.CATEGORY_PARAM_ERROR, msg="参数格式错误: sub_menu_id 应为整数", errors={"sub_menu_id": "invalid"}, status=400)

        sub_sub_menus = Category.objects.filter(parent_id=pid)
        result_list = [m.to_menu_item() for m in sub_sub_menus]
        return CustomResponse(code=Codes.CATEGORY_SUB_SUB_MENU_OK, msg="获取子子菜单成功", data=result_list, status=200)


class ProductTagAPIView(ListAPIView):
    """按标签获取商品列表。路由：/product/tag/<product_tag_id>/<page>/"""

    serializer_class = ProductSerializer

    def list(self, request, *args: Any, **kwargs: Any):
        try:
            page = int(kwargs.get("page"))
            tag_id = int(kwargs.get("product_tag_id"))
        except (TypeError, ValueError):
            return CustomResponse(
                code=Codes.CATEGORY_PARAM_ERROR,  # 复用分类参数错误码
                msg="参数错误，page与product_tag_id应为整数",
                errors={"product_tag_id": "invalid", "page": "invalid"},
                status=400
            )
        if page <= 0:
            return CustomResponse(
                code=Codes.CATEGORY_PARAM_ERROR,
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
                code=Codes.PRODUCT_NOT_FOUND_OR_PARAM_ERROR,
                msg="页面超出范围",
                errors={"page": "out of range"},
                status=404
            )
        page_serialize = self.get_serializer(page.object_list, many=True)
        return CustomResponse(
            code=Codes.PRODUCT_TAG_LIST_OK,
            msg="",
            data=page_serialize.data,
            status=200
        )


class ProductQueryAPIView(APIView):
    """查询商品详情。路由：/product/query/<id>/"""

    def get(self, request, id: int):
        try:
            product_id = int(id)
        except (TypeError, ValueError):
            return CustomResponse(code=Codes.CATEGORY_PARAM_ERROR, msg="参数格式错误: id 应为整数", errors={"id": "invalid"}, status=400)

        try:
            product_data = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return CustomResponse(code=Codes.PRODUCT_NOT_FOUND_OR_PARAM_ERROR, msg="商品不存在", errors={"id": product_id}, status=404)

        result = ProductSerializer(instance=product_data).data
        return CustomResponse(code=Codes.PRODUCT_DETAIL_OK, msg="获取商品详情成功", data=result, status=200)
