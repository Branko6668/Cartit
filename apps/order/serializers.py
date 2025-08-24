from rest_framework import serializers
from apps.order.models import OrderInfo, OrderItem
from django.conf import settings

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_id', 'product_name', 'product_image', 'price', 'quantity', 'total_amount'
        ]

    def _add_prefix(self, path: str | None):
        if not path:
            return path
        if path.startswith('http://') or path.startswith('https://'):
            return path
        base = getattr(settings, 'IMAGE_URL', '') or ''
        return base.rstrip('/') + '/' + path.lstrip('/')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['product_image'] = self._add_prefix(data.get('product_image'))
        return data

class OrderInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = "__all__"

class OrderInfoWithItemsSerializer(OrderInfoSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)

    class Meta(OrderInfoSerializer.Meta):
        fields = OrderInfoSerializer.Meta.fields
