from django.db import models


class ShoppingCart(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='购物车ID')

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        db_column='user_id',
        verbose_name='用户ID'
    )
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.CASCADE,
        db_column='product_id',
        verbose_name='商品ID'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='商品数量'
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='加入时间'
    )
    update_time = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'shopping_cart'
        verbose_name = '购物车'
        verbose_name_plural = '购物车'
        unique_together = (('user', 'product'),)
