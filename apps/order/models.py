# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class OrderInfo(models.Model):
    order_no = models.CharField(unique=True, max_length=32, db_comment='订单编号')
    user = models.ForeignKey('user.User', models.DO_NOTHING, db_comment='用户ID')
    store = models.ForeignKey('store.Store', models.DO_NOTHING, db_comment='店铺ID')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, db_comment='订单总金额')
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, db_comment='优惠金额')
    freight_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, db_comment='运费')
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, db_comment='实付金额')
    status = models.CharField(max_length=15, blank=True, null=True, db_comment='订单状态')
    payment_method = models.CharField(max_length=9, blank=True, null=True, db_comment='支付方式')
    payment_time = models.DateTimeField(blank=True, null=True, db_comment='支付时间')
    ship_time = models.DateTimeField(blank=True, null=True, db_comment='发货时间')
    deliver_time = models.DateTimeField(blank=True, null=True, db_comment='收货时间')
    recipient_name = models.CharField(max_length=50, db_comment='收件人姓名')
    recipient_phone = models.CharField(max_length=11, db_comment='收件人电话')
    recipient_address = models.CharField(max_length=500, db_comment='收件地址')
    remark = models.TextField(blank=True, null=True, db_comment='订单备注')
    create_time = models.DateTimeField(blank=True, null=True, db_comment='创建时间')
    update_time = models.DateTimeField(blank=True, null=True, db_comment='更新时间')

    class Meta:
        managed = False
        db_table = 'order_info'
        db_table_comment = '订单表'


class OrderItem(models.Model):
    order = models.ForeignKey(OrderInfo, models.DO_NOTHING, db_comment='订单ID')
    product = models.ForeignKey('product.Product', models.DO_NOTHING, db_comment='商品ID')
    product_name = models.CharField(max_length=200, db_comment='商品名称（快照）')
    product_image = models.CharField(max_length=500, blank=True, null=True, db_comment='商品图片（快照）')
    price = models.DecimalField(max_digits=12, decimal_places=2, db_comment='商品单价（快照）')
    quantity = models.PositiveIntegerField(db_comment='购买数量')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, db_comment='小计金额')
    create_time = models.DateTimeField(blank=True, null=True, db_comment='创建时间')

    class Meta:
        managed = False
        db_table = 'order_item'
        db_table_comment = '订单商品明细表'
