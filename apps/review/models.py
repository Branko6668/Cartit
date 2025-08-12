from django.db import models

class ProductReview(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='评价ID')

    order = models.ForeignKey(
        'order.OrderInfo',
        on_delete=models.CASCADE,
        db_column='order_id',
        verbose_name='订单ID'
    )
    order_item = models.OneToOneField(
        'order.OrderItem',
        on_delete=models.CASCADE,
        db_column='order_item_id',
        verbose_name='订单商品明细ID'
    )
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
    store = models.ForeignKey(
        'store.Store',
        on_delete=models.CASCADE,
        db_column='store_id',
        verbose_name='店铺ID'
    )
    content = models.TextField(verbose_name='评价内容')
    rating = models.PositiveSmallIntegerField(
        default=5,
        verbose_name='评分（1-5星）'
    )
    images = models.TextField(
        blank=True,
        null=True,
        verbose_name='评价图片（JSON格式）'
    )
    reply_content = models.TextField(
        blank=True,
        null=True,
        verbose_name='商家回复内容'
    )
    reply_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='回复时间'
    )
    is_anonymous = models.BooleanField(
        default=False,
        verbose_name='是否匿名评价'
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='是否删除'
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    update_time = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'product_review'
        verbose_name = '商品评价'
        verbose_name_plural = '商品评价'
        constraints = [
            models.UniqueConstraint(fields=['order_item'], name='uk_order_item'),
            models.CheckConstraint(check=models.Q(rating__gte=1, rating__lte=5), name='chk_rating')
        ]
