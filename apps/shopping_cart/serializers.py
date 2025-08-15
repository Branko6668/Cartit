from rest_framework import serializers
from apps.shopping_cart.models import ShoppingCart

class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    购物车序列化器
    """
    class Meta:
        model = ShoppingCart
        fields = '__all__'

    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product_name'] = instance.product.name
        return representation