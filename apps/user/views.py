from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin
from utils.renderer import CustomResponse
from apps.user.serializers import UserRegisterSerializer, UserMeSerializer, UserAddressSerializer
from apps.user.models import User, UserAddress


class UserRegisterAPIView(APIView):
    """
    用户注册 API 视图
    访问方式：user/register/
    仅处理 POST 请求
    """
    def post(self, request):
        """
        用户注册
        """
        user_serializer = UserRegisterSerializer(data=request.data)
        if not user_serializer.is_valid():
            return CustomResponse(code=4400, msg='请求参数不合法', errors=user_serializer.errors, status=400)
        user = user_serializer.save()
        user_data = UserRegisterSerializer(user)
        return CustomResponse(code=4000, msg='用户操作成功', data=user_data.data, status=200)


class UserLoginAPIView(APIView):
    """
    用户登录 API 视图
    访问方式：user/login/
    仅处理 POST 请求
    """


class UserLogoutAPIView(APIView):
    """
    用户登出 API 视图
    访问方式：user/logout/
    仅处理 POST 请求
    """
    pass

class UserUpdateAPIView(APIView):
    """
    用户更新 API 视图
    访问方式：user/update/
    仅处理 PUT 请求
    """
    pass

class UserDeleteAPIView(APIView):
    """
    用户删除 API 视图
    访问方式：user/delete/
    仅处理 DELETE 请求
    """
    pass

class UserMeAPIView(APIView):
    """
    获取当前用户信息 API 视图
    访问方式：user/me/
    仅处理 GET 请求
    """
    def get(self, request):
        query_me = None
        for key in ['username', 'email', 'phone']:
            value = request.query_params.get(key)
            if value:
                query_me = {key: value}
                break

        if not query_me:
            return CustomResponse(
                code=4400,
                msg='缺少查询参数',
                errors={'detail': '请提供 username, email 或 phone 之一'},
                status=400)

        me_data = User.objects.filter(**query_me, is_deleted=False)
        if not me_data.exists():
            return CustomResponse(
                code=4404,
                msg='用户不存在',
                errors={'detail': '未找到匹配的用户'},
                status=404)
        me_data = me_data.first()
        me_serializer = UserMeSerializer(me_data)
        return CustomResponse(code=4000, msg='获取用户信息成功', data=me_serializer.data, status=200)


class UserAddressAPIView(GenericAPIView, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer
    # lookup_field = "user"
    # #
    # def get_queryset(self):
    #     id = self.kwargs.get("pk")
    #     return self.queryset.filter(pk=id)

    def post(self, request):
        return self.create(request)

    def get(self, request, pk):
        return self.retrieve(request)

    def put(self, request, pk):
        return self.update(request)

    # def delete(self, request, pk):
    #     return self.destroy(request)

class UserAddressListAPIView(GenericAPIView, ListModelMixin):
    serializer_class = UserAddressSerializer

    def get_queryset(self):
        return UserAddress.objects.filter(is_deleted=False)

    def get(self, request):
        return self.list(request)
