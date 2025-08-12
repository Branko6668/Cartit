# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ShoppingCart(models.Model):
    user = models.ForeignKey('user.User', models.DO_NOTHING, db_comment='用户ID')
    product = models.ForeignKey('product.Product', models.DO_NOTHING, db_comment='商品ID')
    quantity = models.PositiveIntegerField(db_comment='商品数量')
    create_time = models.DateTimeField(blank=True, null=True, db_comment='加入时间')
    update_time = models.DateTimeField(blank=True, null=True, db_comment='更新时间')

    class Meta:
        managed = False
        db_table = 'shopping_cart'
        unique_together = (('user', 'product'),)
        db_table_comment = '购物车表'
