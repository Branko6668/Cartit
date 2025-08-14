import json

from django.http import HttpResponse
from django.views import View
from apps.product.models import Category
from utils.ResponseMessage import MenuResponseMessage


class ProductMainMenuView(View):
    """
    商品主菜单视图
    """
    @staticmethod
    def get(request):
        # 处理商品主菜单的 GET 请求
        print('get请求来啦')
        main_menus = Category.objects.filter(parent_id=0)
        result_list = []
        result_json = {}
        for main_menu in main_menus:
            result_json['id'] = main_menu.id
            result_json['name'] = main_menu.name
            result_list.append(result_json)
            result_json = {}
        return MenuResponseMessage.success(result_list)
        # Django 的 HttpResponse 会把这个列表直接转成字符串（调用 str(result_list)）


    @staticmethod
    def post(request):
        # 处理商品主菜单的 POST 请求
        print('post请求来啦')
        return HttpResponse('post请求来啦')


class ProductSubMenuView(View):
    """
    商品子菜单视图
    """
    @staticmethod
    def get(request):
        # 处理商品子菜单的 GET 请求
        print('get请求来啦')
        main_menu_id = request.GET.get('main_menu_id')
        sub_menus = Category.objects.filter(parent_id=main_menu_id)
        result_list = []
        result_json = {}
        for sub_menu in sub_menus:
            result_json['id'] = sub_menu.id
            result_json['name'] = sub_menu.name
            result_list.append(result_json)
            result_json = {}
        return MenuResponseMessage.success(result_list)

    @staticmethod
    def post(request):
        # 处理商品子菜单的 POST 请求
        print('post请求来啦')
        return HttpResponse('post请求来啦')

class ProductSubSubMenuView(View):
    """
    商品子子菜单视图
    """
    @staticmethod
    def get(request):
        # 处理商品子子菜单的 GET 请求
        print('get请求来啦')
        sub_menu_id = request.GET.get('sub_menu_id')
        sub_sub_menus = Category.objects.filter(parent_id=sub_menu_id)
        result_list = []
        result_json = {}
        for sub_sub_menu in sub_sub_menus:
            result_json['id'] = sub_sub_menu.id
            result_json['name'] = sub_sub_menu.name
            result_list.append(result_json)
            result_json = {}
        return MenuResponseMessage.success(result_list)

    @staticmethod
    def post(request):
        # 处理商品子子菜单的 POST 请求
        print('post请求来啦')
        return HttpResponse('post请求来啦')


