from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from apps.user.models import User
from django.contrib.auth.hashers import make_password


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
    password = serializers.CharField(write_only=False)  # 会覆盖 extra_kwargs 的设置
    birthday = serializers.DateField(format="%Y-%m-%d",required=False)
    avatar_url = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        print("create方法被调用")
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