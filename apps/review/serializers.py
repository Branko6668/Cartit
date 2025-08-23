from rest_framework import serializers
from django.conf import settings
from .models import ProductReview
import json

class ImagesField(serializers.Field):
    """仅支持字符串列表输入：
    - [] 空列表
    - ["path1", "path2"] 一个或多个
    其它类型（单字符串、JSON字符串、数字等）一律报错。
    输出统一为字符串列表。
    """
    def to_internal_value(self, value):
        if value is None:
            return []
        if isinstance(value, list):
            # 允许空列表
            if not all(isinstance(x, str) and x.strip() for x in value):
                raise serializers.ValidationError("images 必须是非空字符串的列表，或空列表 []")
            # 去除首尾空白
            return [x.strip() for x in value]
        raise serializers.ValidationError("images 仅支持列表，例如 [] 或 [\"static/review_images/01.png\"]")

    def to_representation(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            # 存储层是 JSON 字符串时进行解析
            try:
                data = json.loads(value)
                if isinstance(data, list) and all(isinstance(x, str) for x in data):
                    return data
            except Exception:
                pass
            return []
        return []

class ProductReviewSerializer(serializers.ModelSerializer):
    images = ImagesField(required=False, allow_null=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        exclude = ['is_deleted']  # 不暴露软删除字段
        read_only_fields = ['id', 'create_time', 'update_time', 'reply_time']
        extra_kwargs = {
            'order': {'read_only': True},
            'user': {'read_only': True},
            'product': {'read_only': True},
            'store': {'read_only': True},
        }

    def _add_prefix(self, path: str | None):
        if not path:
            return path
        if path.startswith('http://') or path.startswith('https://'):
            return path
        base = getattr(settings, 'IMAGE_URL', '') or ''
        return base.rstrip('/') + '/' + path.lstrip('/')

    def get_user_avatar_url(self, obj: ProductReview):
        return self._add_prefix(getattr(obj.user, 'avatar_url', None))

    def validate(self, attrs):
        order_item = attrs.get('order_item')
        if order_item is None:
            raise serializers.ValidationError({'order_item': 'required'})
        # 防重复评论：OneToOne 基本能保证，这里提前给出友好错误
        if ProductReview.objects.filter(order_item=order_item).exists():
            raise serializers.ValidationError({'order_item': '该订单明细已评价'})
        # 若使用了认证，则校验归属
        req = self.context.get('request')
        if req and getattr(req, 'user', None) and req.user.is_authenticated:
            if getattr(order_item.order, 'user_id', None) != req.user.id:
                raise serializers.ValidationError({'order_item': '无权评价该订单明细'})
        return attrs

    def create(self, validated_data):
        # 统一处理 images 存储（列表 -> JSON字符串）
        imgs = validated_data.pop('images', [])
        validated_data['images'] = json.dumps(imgs, ensure_ascii=False)

        order_item = validated_data['order_item']
        order = order_item.order
        product = order_item.product
        user = order.user
        store = order.store

        validated_data.update({
            'order': order,
            'product': product,
            'user': user,
            'store': store,
        })
        return super().create(validated_data)

    def update(self, instance, validated_data):
        marker = object()
        imgs = validated_data.pop('images', marker)
        if imgs is not marker:
            validated_data['images'] = json.dumps(imgs or [], ensure_ascii=False)
        # order/order_item/user/product/store 不允许在更新中被修改
        for k in ('order', 'order_item', 'user', 'product', 'store'):
            validated_data.pop(k, None)
        return super().update(instance, validated_data)
