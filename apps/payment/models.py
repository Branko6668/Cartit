# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Payment(models.Model):
    payment_no = models.CharField(unique=True, max_length=32, db_comment='支付流水号')
    order = models.ForeignKey('order.OrderInfo', models.DO_NOTHING, db_comment='订单ID')
    user = models.ForeignKey('user.User', models.DO_NOTHING, db_comment='用户ID')
    amount = models.DecimalField(max_digits=12, decimal_places=2, db_comment='支付金额')
    payment_method = models.CharField(max_length=9, db_comment='支付方式')
    payment_channel = models.CharField(max_length=50, blank=True, null=True, db_comment='支付渠道')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, db_comment='第三方交易号')
    status = models.CharField(max_length=9, blank=True, null=True, db_comment='支付状态')
    paid_time = models.DateTimeField(blank=True, null=True, db_comment='支付完成时间')
    notify_time = models.DateTimeField(blank=True, null=True, db_comment='回调通知时间')
    create_time = models.DateTimeField(blank=True, null=True, db_comment='创建时间')

    class Meta:
        managed = False
        db_table = 'payment'
        db_table_comment = '支付记录表'
