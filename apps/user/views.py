"""
User 模块视图

包含：
- 用户注册/登录/登出/更新/注销
- 查询当前用户信息（支持 username/email/phone）
- 用户地址的增删改查与列表

所有接口统一返回 CustomResponse，鉴权与 JWT 可在后续接入。
"""
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
from utils.error_codes import Codes
from django.core.cache import cache
import re, random, logging


class UserRegisterAPIView(APIView):
    """
    用户注册 API 视图
    路由：/user/register/
    方法：POST
    需要字段：phone, password, code (+ 可选 username/email/avatar_url 等)
    """
    def post(self, request: Request):
        phone = request.data.get('phone', '').strip()
        code = request.data.get('code', '').strip()
        if not phone:
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='手机号不能为空', errors={'phone': 'required'}, status=400)
        if not code:
            return CustomResponse(code=Codes.VERIFICATION_CODE_INVALID, msg='验证码不能为空', errors={'code': 'required'}, status=400)
        # 校验验证码
        code_key = f'vc:code:{phone}'
        stored = cache.get(code_key)
        if stored is None:
            return CustomResponse(code=Codes.VERIFICATION_CODE_EXPIRED, msg='验证码已失效', status=400)
        if stored != code:
            return CustomResponse(code=Codes.VERIFICATION_CODE_INVALID, msg='验证码错误', status=400)

        user_serializer = UserRegisterSerializer(data=request.data)
        if not user_serializer.is_valid():
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='请求参数不合法', errors=user_serializer.errors, status=400)
        user = user_serializer.save()
        # 使用后失效验证码
        cache.delete(code_key)
        user_data = UserMeSerializer(user)
        return CustomResponse(code=Codes.USER_ACTION_OK, msg='用户注册成功', data=user_data.data, status=200)


class UserLoginAPIView(GenericAPIView):
    """
    用户登录 API 视图
    路由：/user/login/
    方法：POST
    """
    def post(self, request: Request):
        phone = request.data.get("phone")
        password = request.data.get("password")
        if not phone:
            return CustomResponse(code=Codes.LOGIN_PHONE_EMPTY, msg="手机号不能为空", status=400)
        if not password:
            return CustomResponse(code=Codes.LOGIN_PASSWORD_EMPTY, msg="密码不能为空", status=400)

        try:
            user = User.objects.get(phone=phone, is_deleted=False)
        except ObjectDoesNotExist:
            return CustomResponse(code=Codes.LOGIN_PHONE_NOT_REGISTERED, msg="该手机号未注册", status=400)

        if user.status != 'active':
            return CustomResponse(code=Codes.LOGIN_USER_DISABLED, msg="账户已禁用", status=403)

        if not check_password(password, user.password):
            return CustomResponse(code=Codes.LOGIN_CREDENTIALS_INVALID, msg="手机号或密码错误", status=400)

        token = generate_token(user_id=user.id, username=user.username)
        user_serializer = UserMeSerializer(instance=user)
        return CustomResponse(code=Codes.USER_ACTION_OK, msg="登录成功", data={"token": token, "user": user_serializer.data}, status=200)


class UserLogoutAPIView(APIView):
    """
    用户登出 API 视图
    路由：/user/logout/
    方法：POST
    """
    def post(self, request: Request):
        return CustomResponse(code=Codes.USER_ACTION_OK, msg="登出成功", data=None, status=200)


class UserUpdateAPIView(APIView):
    """
    用户资料更新 API 视图
    路由：/user/update/
    方法：PUT
    """
    def put(self, request: Request):
        user_id = request.data.get("id")
        if not user_id:
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg="缺少用户ID", errors={"id": "必填"}, status=400)

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
            return CustomResponse(code=Codes.USER_UPDATE_FAILED, msg="用户信息更新失败", errors={"detail": str(e)}, status=400)

        return CustomResponse(code=Codes.USER_ACTION_OK, msg="用户信息更新成功", data=UserMeSerializer(user).data, status=200)


class UserDeleteAPIView(APIView):
    """
    用户注销 API 视图（软删除：is_deleted=True, status=disabled）
    路由：/user/delete/
    方法：DELETE
    """
    def delete(self, request: Request):
        user_id = request.query_params.get("id") or request.data.get("id")
        if not user_id:
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg="缺少用户ID", errors={"id": "必填"}, status=400)

        user = get_object_or_404(User, pk=user_id, is_deleted=False)
        user.is_deleted = True
        user.status = 'disabled'
        user.save(update_fields=["is_deleted", "status"])
        return CustomResponse(code=Codes.USER_ACTION_OK, msg="用户已注销", data=None, status=200)


class UserMeAPIView(APIView):
    """
    获取当前用户信息 API 视图
    路由：/user/me/
    方法：GET
    支持通过 username/email/phone 三选一查询
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
                code=Codes.USER_PARAM_INVALID,
                msg='缺少查询参数',
                errors={'detail': '请提供 username, email 或 phone 之一'},
                status=400)

        me_data = User.objects.filter(**query_me, is_deleted=False)
        if not me_data.exists():
            return CustomResponse(
                code=Codes.USER_NOT_FOUND,
                msg='用户不存在',
                errors={'detail': '未找到匹配的用户'},
                status=404)
        me_data = me_data.first()
        me_serializer = UserMeSerializer(me_data)
        return CustomResponse(code=Codes.USER_ACTION_OK, msg='获取用户信息成功', data=me_serializer.data, status=200)


class UserAddressCreateAPIView(GenericAPIView, CreateModelMixin):
    """创建用户地址。

    路由：
      - POST /user/address/
    """

    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='请求参数不合法', errors=serializer.errors, status=400)
        instance = serializer.save()
        return CustomResponse(code=Codes.USER_ACTION_OK, msg='创建地址成功', data=self.get_serializer(instance).data, status=200)


class UserAddressDetailAPIView(GenericAPIView, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    """用户地址详情的查询/更新/删除。

    路由：
      - GET    /user/address/<pk>/
      - PUT    /user/address/<pk>/
      - DELETE /user/address/<pk>/
    """

    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer

    def get(self, request: Request, pk: int):
        instance = get_object_or_404(UserAddress, pk=pk, is_deleted=False)
        return CustomResponse(code=Codes.USER_ACTION_OK, msg='获取地址成功', data=self.get_serializer(instance).data, status=200)

    def put(self, request: Request, pk: int):
        instance = get_object_or_404(UserAddress, pk=pk, is_deleted=False)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='请求参数不合法', errors=serializer.errors, status=400)
        instance = serializer.save()
        return CustomResponse(code=Codes.USER_ACTION_OK, msg='更新地址成功', data=self.get_serializer(instance).data, status=200)

    def delete(self, request: Request, pk: int):
        instance = get_object_or_404(UserAddress, pk=pk, is_deleted=False)
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
        return CustomResponse(code=Codes.USER_ACTION_OK, msg='删除地址成功', data=None, status=200)


class UserAddressListAPIView(GenericAPIView, ListModelMixin):
    """获取用户地址列表（支持按 user 或 user_id 过滤）。"""

    serializer_class = UserAddressSerializer

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
        return CustomResponse(code=Codes.USER_ACTION_OK, msg='获取地址列表成功', data=serializer.data, status=200)


class UserSendCodeAPIView(APIView):
    """发送手机验证码（本地调试：直接打印在控制台）
    路由：POST /user/send_code/
    请求：{"phone": "13800000000", "scene": "register|login|reset"}
    节流：同一手机号 60s 只能发送一次；验证码有效期 5 分钟
    """
    def post(self, request: Request):
        phone = request.data.get('phone', '').strip()
        scene = (request.data.get('scene') or 'login').strip()
        if not phone:
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='手机号不能为空', errors={'phone': 'required'}, status=400)
        if not re.fullmatch(r'^1\d{10}$', phone):
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='手机号格式不正确', errors={'phone': 'invalid'}, status=400)
        throttle_key = f'vc:ttl:{phone}'
        if cache.get(throttle_key):
            return CustomResponse(code=Codes.VERIFICATION_CODE_THROTTLED, msg='发送过于频繁，请稍后再试', status=429)
        code_key = f'vc:code:{phone}'
        code = f"{random.randint(100000, 999999)}"
        cache.set(code_key, code, 300)        # 验证码 5 分钟有效
        cache.set(throttle_key, 1, 60)        # 60 秒节流
        logging.getLogger(__name__).info(f"[VCODE] phone={phone} scene={scene} code={code}")
        print(f"[DEBUG VCODE] {phone} -> {code}")
        return CustomResponse(code=Codes.VERIFICATION_CODE_SENT, msg='验证码已发送', data={'phone': phone[:-4] + '****', 'scene': scene}, status=200)


class UserResetPasswordAPIView(APIView):
    """重置密码接口
    路由：POST /user/reset_password/
    请求：{"phone": "13800000000", "code": "123456", "new_password": "Passw0rd!"}
    说明：本地环境验证码通过控制台查看；成功后旧验证码失效
    """
    def post(self, request: Request):
        phone = request.data.get('phone', '').strip()
        code = request.data.get('code', '').strip()
        new_password = request.data.get('new_password')
        if not (phone and code and new_password):
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='缺少必要字段', errors={'phone': 'required', 'code': 'required', 'new_password': 'required'}, status=400)
        if not re.fullmatch(r'^1\d{10}$', phone):
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='手机号格式不正确', errors={'phone': 'invalid'}, status=400)
        if len(new_password) < 6:
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='密码至少 6 位', errors={'new_password': 'too_short'}, status=400)
        code_key = f'vc:code:{phone}'
        stored = cache.get(code_key)
        if stored is None:
            return CustomResponse(code=Codes.VERIFICATION_CODE_EXPIRED, msg='验证码已失效', status=400)
        if stored != code:
            return CustomResponse(code=Codes.VERIFICATION_CODE_INVALID, msg='验证码错误', status=400)
        try:
            user = User.objects.get(phone=phone, is_deleted=False)
        except User.DoesNotExist:
            return CustomResponse(code=Codes.PASSWORD_RESET_PHONE_NOT_FOUND, msg='手机号未注册', status=404)
        user.password = make_password(new_password)
        user.save(update_fields=['password'])
        cache.delete(code_key)
        return CustomResponse(code=Codes.PASSWORD_RESET_OK, msg='密码重置成功', data={'user_id': user.id}, status=200)
