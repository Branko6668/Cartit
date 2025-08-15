from django.contrib.messages.api import success
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.product.models import Category
from apps.product.models import Product
from utils.ResponseMessage import MenuResponseMessage
from utils.ResponseMessage import ProductResponseMessage
from apps.product.serializers import ProductSerializer, CategorySerializer


class ProductMainMenuView(APIView):
    """
    商品主菜单视图
    访问方式：product/main_menu/
    处理 GET 和 POST 请求
    """
    @staticmethod
    def get(request):
        # 处理商品主菜单的 GET 请求
        print('get请求来啦')
        main_menus = Category.objects.filter(parent_id=0)
        result_list = [m.to_menu_item() for m in main_menus]
        return Response(result_list)
        # Django 的 HttpResponse 会把这个列表直接转成字符串（调用 str(result_list)）



class ProductSubMenuView(APIView):
    """
    商品子菜单视图
    访问方式：product/sub_menu/
    处理 GET 和 POST 请求
    """
    @staticmethod
    def get(request):
        # 处理商品子菜单的 GET 请求
        print('get请求来啦')
        main_menu_id = request.GET.get('main_menu_id')
        sub_menus = Category.objects.filter(parent_id=main_menu_id)
        result_list = [m.to_menu_item() for m in sub_menus]
        return Response(result_list)

class ProductSubSubMenuView(APIView):
    """
    商品子子菜单视图
    访问方式：product/sub_sub_menu/
    处理 GET 和 POST 请求
    """
    @staticmethod
    def get(request):
        # 处理商品子子菜单的 GET 请求
        print('get请求来啦')
        sub_menu_id = request.GET.get('sub_menu_id')
        sub_sub_menus = Category.objects.filter(parent_id=sub_menu_id)
        result_list = [m.to_menu_item() for m in sub_sub_menus]
        return Response(result_list)


class ProductTagAPIView(APIView):
    """
    商品标签 API 视图
    访问方式：product/tags/[product_tag_id]
    处理 GET 和 POST 请求
    """

    def get(self, request, product_tag_id, page):
        start = (int(page) - 1) * 20
        end = int(page) * 20
        products = Product.objects.filter(tags__id=product_tag_id)
        paged_products = products[start:end]
        serialized_data = ProductSerializer(instance=paged_products, many=True).data
        return Response(serialized_data)


class ProductQueryAPIView(APIView):
    """
    商品查询 API 视图
    访问方式：product/query/
    处理 GET 和 POST 请求
    """
    def get(self, request, id):
        # 处理商品查询的 GET 请求
        print('get请求来啦')
        product_data = Product.objects.get(id=id)
        result = ProductSerializer(instance=product_data).data
        return Response(result)
