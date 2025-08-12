from django.db import models


class OrderInfo(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='订单ID')

    order_no = models.CharField(max_length=32, unique=True, verbose_name='订单编号')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, db_column='user_id', verbose_name='用户ID')
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, db_column='store_id', verbose_name='店铺ID')

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='订单总金额')
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='优惠金额')
    freight_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='运费')
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='实付金额')

    status = models.CharField(
        max_length=15,
        choices=[
            ('pending_payment', '待支付'),
            ('paid', '已支付'),
            ('shipped', '已发货'),
            ('delivered', '已收货'),
            ('completed', '已完成'),
            ('cancelled', '已取消'),
            ('refunded', '已退款')
        ],
        default='pending_payment',
        verbose_name='订单状态'
    )
    payment_method = models.CharField(
        max_length=9,
        choices=[
            ('alipay', '支付宝'),
            ('wechat', '微信支付'),
            ('bank_card', '银行卡'),
            ('cash', '现金')
        ],
        blank=True,
        null=True,
        verbose_name='支付方式'
    )
    payment_time = models.DateTimeField(blank=True, null=True, verbose_name='支付时间')
    ship_time = models.DateTimeField(blank=True, null=True, verbose_name='发货时间')
    deliver_time = models.DateTimeField(blank=True, null=True, verbose_name='收货时间')

    recipient_name = models.CharField(max_length=50, verbose_name='收件人姓名')
    recipient_phone = models.CharField(max_length=11, verbose_name='收件人电话')
    recipient_address = models.CharField(max_length=500, verbose_name='收件地址')
    remark = models.TextField(blank=True, null=True, verbose_name='订单备注')

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'order_info'
        verbose_name = '订单'
        verbose_name_plural = '订单'


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='明细ID')

    order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, db_column='order_id', verbose_name='订单ID')
    product = models.ForeignKey('product.Product', on_delete=models.PROTECT, db_column='product_id', verbose_name='商品ID')

    product_name = models.CharField(max_length=200, verbose_name='商品名称（快照）')
    product_image = models.CharField(max_length=500, blank=True, null=True, verbose_name='商品图片（快照）')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='商品单价（快照）')
    quantity = models.PositiveIntegerField(verbose_name='购买数量')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='小计金额')

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'order_item'
        verbose_name = '订单商品明细'
        verbose_name_plural = '订单商品明细'
