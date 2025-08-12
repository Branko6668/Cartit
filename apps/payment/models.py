from django.db import models

class Payment(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='支付记录ID')

    payment_no = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='支付流水号'
    )
    order = models.ForeignKey(
        'order.OrderInfo',
        on_delete=models.CASCADE,
        db_column='order_id',
        verbose_name='订单ID'
    )
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        db_column='user_id',
        verbose_name='用户ID'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='支付金额'
    )
    payment_method = models.CharField(
        max_length=9,
        choices=[
            ('alipay', '支付宝'),
            ('wechat', '微信支付'),
            ('bank_card', '银行卡'),
            ('cash', '现金')
        ],
        verbose_name='支付方式'
    )
    payment_channel = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='支付渠道'
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='第三方交易号'
    )
    status = models.CharField(
        max_length=9,
        choices=[
            ('pending', '待支付'),
            ('success', '支付成功'),
            ('failed', '支付失败'),
            ('cancelled', '已取消')
        ],
        default='pending',
        verbose_name='支付状态'
    )
    paid_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='支付完成时间'
    )
    notify_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='回调通知时间'
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'payment'
        verbose_name = '支付记录'
        verbose_name_plural = '支付记录'
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gte=0), name='chk_payment_amount')
        ]