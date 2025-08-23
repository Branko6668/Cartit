from rest_framework import serializers
from django.conf import settings
from apps.shopping_cart.models import ShoppingCart

class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    购物车序列化器：附加商品与店铺信息、金额、图片前缀
    """
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def _add_prefix(self, path: str | None):
        if not path:
            return path
        if path.startswith('http://') or path.startswith('https://'):
            return path
        base = getattr(settings, 'IMAGE_URL', '') or ''
        return base.rstrip('/') + '/' + path.lstrip('/')

    def to_representation(self, instance: ShoppingCart):
        p = instance.product
        rep = super().to_representation(instance)
        rep.update({
            'product_name': p.name,
            'product_image': self._add_prefix(p.thumbnail),
            'unit_price': str(p.price),
            'original_price': str(p.original_price) if p.original_price is not None else None,
            'stock': p.stock,
            'is_off_shelf': p.status in ('off_sale', 'out_of_stock'),
            'store_id': p.store_id,
            'store_name': getattr(p.store, 'store_name', None),
            'amount': str(p.price * instance.quantity),
        })
        return rep
