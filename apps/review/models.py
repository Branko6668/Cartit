# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ProductReview(models.Model):
    order = models.ForeignKey('order.OrderInfo', models.DO_NOTHING, db_comment='订单ID')
    order_item = models.OneToOneField('order.OrderItem', models.DO_NOTHING, db_comment='订单商品明细ID')
    user = models.ForeignKey('user.User', models.DO_NOTHING, db_comment='用户ID')
    product = models.ForeignKey('product.Product', models.DO_NOTHING, db_comment='商品ID')
    store = models.ForeignKey('store.Store', models.DO_NOTHING, db_comment='店铺ID')
    content = models.TextField(db_comment='评价内容')
    rating = models.PositiveIntegerField(db_comment='评分（1-5星）')
    images = models.TextField(blank=True, null=True, db_comment='评价图片（JSON格式）')
    reply_content = models.TextField(blank=True, null=True, db_comment='商家回复内容')
    reply_time = models.DateTimeField(blank=True, null=True, db_comment='回复时间')
    is_anonymous = models.IntegerField(blank=True, null=True, db_comment='是否匿名评价')
    is_deleted = models.IntegerField(blank=True, null=True, db_comment='是否删除')
    create_time = models.DateTimeField(blank=True, null=True, db_comment='创建时间')
    update_time = models.DateTimeField(blank=True, null=True, db_comment='更新时间')

    class Meta:
        managed = False
        db_table = 'product_review'
        db_table_comment = '商品评价表'
