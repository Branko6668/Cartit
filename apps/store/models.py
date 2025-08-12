# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Store(models.Model):
    store_name = models.CharField(unique=True, max_length=100, db_comment='店铺名称')
    owner = models.ForeignKey('user.User', models.DO_NOTHING, db_comment='店主用户ID')
    description = models.TextField(blank=True, null=True, db_comment='店铺描述')
    logo_url = models.CharField(max_length=500, blank=True, null=True, db_comment='店铺Logo URL')
    contact_phone = models.CharField(max_length=11, blank=True, null=True, db_comment='联系电话')
    business_license = models.CharField(max_length=100, blank=True, null=True, db_comment='营业执照号')
    status = models.CharField(max_length=9, blank=True, null=True, db_comment='店铺状态')
    is_deleted = models.IntegerField(blank=True, null=True, db_comment='是否删除')
    create_time = models.DateTimeField(blank=True, null=True, db_comment='创建时间')
    update_time = models.DateTimeField(blank=True, null=True, db_comment='更新时间')

    class Meta:
        managed = False
        db_table = 'store'
        db_table_comment = '店铺信息表'
