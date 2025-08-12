# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class User(models.Model):
    username = models.CharField(unique=True, max_length=50, db_comment='用户名（登录用）')
    name = models.CharField(max_length=100, blank=True, null=True, db_comment='真实姓名')
    phone = models.CharField(unique=True, max_length=11, blank=True, null=True, db_comment='手机号')
    email = models.CharField(unique=True, max_length=100, blank=True, null=True, db_comment='邮箱')
    password = models.CharField(max_length=255, db_comment='密码（加密存储）')
    avatar_url = models.CharField(max_length=500, blank=True, null=True, db_comment='头像URL')
    gender = models.CharField(max_length=6, blank=True, null=True, db_comment='性别')
    birthday = models.DateField(blank=True, null=True, db_comment='生日')
    status = models.CharField(max_length=8, blank=True, null=True, db_comment='账户状态')
    is_deleted = models.IntegerField(blank=True, null=True, db_comment='是否删除（软删除）')
    create_time = models.DateTimeField(blank=True, null=True, db_comment='创建时间')
    update_time = models.DateTimeField(blank=True, null=True, db_comment='更新时间')

    class Meta:
        managed = False
        db_table = 'user'
        db_table_comment = '用户信息表'


class UserAddress(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING, db_comment='用户ID')
    recipient_name = models.CharField(max_length=50, db_comment='收件人姓名')
    recipient_phone = models.CharField(max_length=11, db_comment='收件人电话')
    province = models.CharField(max_length=20, db_comment='省份')
    city = models.CharField(max_length=20, db_comment='城市')
    district = models.CharField(max_length=20, db_comment='区县')
    detail_address = models.CharField(max_length=200, db_comment='详细地址')
    postal_code = models.CharField(max_length=10, blank=True, null=True, db_comment='邮政编码')
    is_default = models.IntegerField(blank=True, null=True, db_comment='是否默认地址')
    is_deleted = models.IntegerField(blank=True, null=True, db_comment='是否删除')
    create_time = models.DateTimeField(blank=True, null=True, db_comment='创建时间')
    update_time = models.DateTimeField(blank=True, null=True, db_comment='更新时间')

    class Meta:
        managed = False
        db_table = 'user_address'
        db_table_comment = '用户地址表'