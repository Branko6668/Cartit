from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.request import Request
from utils.renderer import CustomResponse
from apps.user.serializers import UserRegisterSerializer, UserMeSerializer, UserAddressSerializer
from apps.user.models import User, UserAddress
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.contrib.auth.hashers import check_password, make_password
from utils.jwt_auth import generate_token
from rest_framework.permissions import IsAuthenticated


class UserRegisterAPIView(APIView):
    """
    用户注册 API 视图
    访问方式：user/register/
    仅处理 POST 请求
    """
    def post(self, request: Request):
        user_serializer = UserRegisterSerializer(data=request.data)
        if not user_serializer.is_valid():
            return CustomResponse(code=4400, msg='请求参数不合法', errors=user_serializer.errors, status=400)
        user = user_serializer.save()
        user_data = UserMeSerializer(user)
        return CustomResponse(code=4000, msg='用户操作成功', data=user_data.data, status=200)


class UserLoginAPIView(GenericAPIView):
    """
    用户登录 API 视图
    访问方式：user/login/
    仅处理 POST 请求
    """
    def post(self, request: Request):
        phone = request.data.get("phone")
        password = request.data.get("password")
        if not phone:
            return CustomResponse(code=4401, msg="手机号不能为空", status=400)
        if not password:
            return CustomResponse(code=4402, msg="密码不能为空", status=400)

        try:
            user = User.objects.get(phone=phone, is_deleted=False)
        except ObjectDoesNotExist:
            return CustomResponse(code=4403, msg="该手机号未注册", status=400)

        if user.status != 'active':
            return CustomResponse(code=4405, msg="账户已禁用", status=403)

        if not check_password(password, user.password):
            return CustomResponse(code=4406, msg="手机号或密码错误", status=400)

        token = generate_token(user_id=user.id, username=user.username)
        user_serializer = UserMeSerializer(instance=user)
        return CustomResponse(code=4000, msg="登录成功", data={"token": token, "user": user_serializer.data}, status=200)


class UserLogoutAPIView(APIView):
    """
    用户登出 API 视图
    访问方式：user/logout/
    仅处理 POST 请求
    """
    def post(self, request: Request):
        return CustomResponse(code=4000, msg="登出成功", data=None, status=200)


class UserUpdateAPIView(APIView):
    """
    用户更新 API 视图
    访问方式：user/update/
    仅处理 PUT 请求
    """
    def put(self, request: Request):
        user_id = request.data.get("id")
        if not user_id:
            return CustomResponse(code=4400, msg="缺少用户ID", errors={"id": "必填"}, status=400)

        user = get_object_or_404(User, pk=user_id, is_deleted=False)

        updatable_fields = [
            "username", "name", "phone", "email", "avatar_url", "gender", "birthday"
        ]
        for field in updatable_fields:
            if field in request.data:
                setattr(user, field, request.data.get(field))

        if request.data.get("password"):
            user.password = make_password(request.data.get("password"))

        try:
            user.save()
        except IntegrityError as e:
            return CustomResponse(code=4407, msg="用户信息更新失败", errors={"detail": str(e)}, status=400)

        return CustomResponse(code=4000, msg="用户信息更新成功", data=UserMeSerializer(user).data, status=200)


class UserDeleteAPIView(APIView):
    """
    用户注销 API 视图
    访问方式：user/delete/
    仅处理 DELETE 请求
    """
    def delete(self, request: Request):
        user_id = request.query_params.get("id") or request.data.get("id")
        if not user_id:
            return CustomResponse(code=4400, msg="缺少用户ID", errors={"id": "必填"}, status=400)

        user = get_object_or_404(User, pk=user_id, is_deleted=False)
        user.is_deleted = True
        user.status = 'disabled'
        user.save(update_fields=["is_deleted", "status"])
        return CustomResponse(code=4000, msg="用户已注销", data=None, status=200)


class UserMeAPIView(APIView):
    """
    获取当前用户信息 API 视图
    访问方式：user/me/
    仅处理 GET 请求
    """
    def get(self, request: Request):
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

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(code=4400, msg='请求参数不合法', errors=serializer.errors, status=400)
        instance = serializer.save()
        return CustomResponse(code=4000, msg='创建地址成功', data=self.get_serializer(instance).data, status=200)

    def get(self, request: Request, pk):
        instance = get_object_or_404(UserAddress, pk=pk, is_deleted=False)
        return CustomResponse(code=4000, msg='获取地址成功', data=self.get_serializer(instance).data, status=200)

    def put(self, request: Request, pk):
        instance = get_object_or_404(UserAddress, pk=pk, is_deleted=False)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return CustomResponse(code=4400, msg='请求参数不合法', errors=serializer.errors, status=400)
        instance = serializer.save()
        return CustomResponse(code=4000, msg='更新地址成功', data=self.get_serializer(instance).data, status=200)

    def delete(self, request: Request, pk):
        instance = get_object_or_404(UserAddress, pk=pk, is_deleted=False)
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
        return CustomResponse(code=4000, msg='删除地址成功', data=None, status=200)


class UserAddressListAPIView(GenericAPIView, ListModelMixin):
    serializer_class = UserAddressSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = UserAddress.objects.filter(is_deleted=False)
        query_dict = getattr(self.request, "query_params", None) or self.request.GET
        user_id = query_dict.get("user") or query_dict.get("user_id")
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

    def get(self, request: Request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(code=4000, msg='获取地址列表成功', data=serializer.data, status=200)
