from rest_framework import serializers
from django.conf import settings
from core.settings import IMAGE_URL
from apps.product.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    商品序列化器：自动为 thumbnail 补全 IMAGE_URL 前缀，并提供 image_url 兼容字段
    """
    image_url = serializers.SerializerMethodField()
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Product
        fields = '__all__'

    def _add_prefix(self, path: str | None) -> str | None:
        if not path:
            return path
        if path.startswith('http://') or path.startswith('https://'):
            return path
        base = getattr(settings, 'IMAGE_URL', '') or ''
        return base.rstrip('/') + '/' + path.lstrip('/')

    def get_image_url(self, product: Product):
        return self._add_prefix(product.thumbnail)

    def to_representation(self, instance: Product):
        data = super().to_representation(instance)
        # 覆盖原 thumbnail 字段为带前缀完整 URL
        data['thumbnail'] = self._add_prefix(data.get('thumbnail'))
        # 若 gallery 为 JSON 数组字符串，可尝试补全里面的相对路径（可选）
        # 简单处理：仅当是以 [ 开头并包含 .png/.jpg 等关键字时尝试解析
        gallery = data.get('gallery')
        if isinstance(gallery, str) and gallery.strip().startswith('['):
            try:
                import json
                imgs = json.loads(gallery)
                if isinstance(imgs, list):
                    data['gallery'] = [self._add_prefix(i) for i in imgs]
            except Exception:
                pass  # 原样返回
        return data


class CategorySerializer(serializers.Serializer):
    """
    分类序列化器
    """

    id = serializers.IntegerField()
    name = serializers.CharField(max_length=50)
    parent_id = serializers.IntegerField(default=0)
    sort_order = serializers.IntegerField(default=0)
    icon_url = serializers.CharField(max_length=500, allow_blank=True, allow_null=True)
    is_active = serializers.BooleanField(default=True)
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')