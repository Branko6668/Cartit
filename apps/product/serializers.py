from rest_framework import serializers
from core.settings import IMAGE_URL
from apps.product.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    商品序列化器
    """
    class Meta:
        model = Product
        fields = '__all__'
    image_url = serializers.SerializerMethodField()
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    def get_image_url(self, product):
        new_image_url = IMAGE_URL + product.thumbnail
        return new_image_url

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