from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from apps.user.models import User, UserAddress
from django.contrib.auth.hashers import make_password
import re
from django.conf import settings


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    """
    username = serializers.CharField(
        allow_blank=True,
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all(), message="用户名已存在")]
    )
    phone = serializers.CharField(
        allow_blank=False,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="手机号已存在")]
    )
    email = serializers.CharField(
        allow_blank=True,
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all(), message="邮箱已存在")]
    )
    password = serializers.CharField(write_only=True)  # 会覆盖 extra_kwargs 的设置
    birthday = serializers.DateField(format="%Y-%m-%d",required=False)
    avatar_url = serializers.CharField(required=False, allow_blank=True)

    def validate_phone(self, value):
        if not re.fullmatch(r'^1\d{10}$', value):
            raise serializers.ValidationError("手机号格式不正确")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("密码至少6位")
        if not re.search(r'[A-Za-z]', value) or not re.search(r'\d', value):
            raise serializers.ValidationError("密码需包含字母和数字")
        return value

    def create(self, validated_data):
        # print("create方法被调用")
        # 对密码进行加密处理
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user


    class Meta:
        model = User
        fields = "__all__"


class UserMeSerializer(serializers.ModelSerializer):
    """
    当前用户信息序列化器
    """
    birthday = serializers.DateField(format="%Y-%m-%d", required=False)

    class Meta:
        model = User
        exclude = ['password', 'is_deleted', 'create_time', 'update_time', 'status']

    def _add_prefix(self, path: str | None):
        if not path:
            return path
        if path.startswith('http://') or path.startswith('https://'):
            return path
        base = getattr(settings, 'IMAGE_URL', '') or ''
        return base.rstrip('/') + '/' + path.lstrip('/')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['avatar_url'] = self._add_prefix(data.get('avatar_url'))
        return data


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = "__all__"