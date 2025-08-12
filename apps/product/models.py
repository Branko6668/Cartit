# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Product(models.Model):
    category = models.ForeignKey('product.Category', models.DO_NOTHING, db_comment='分类ID')
    store = models.ForeignKey('store.Store', models.DO_NOTHING, db_comment='店铺ID')
    name = models.CharField(max_length=200, db_comment='商品名称')
    subtitle = models.CharField(max_length=500, blank=True, null=True, db_comment='商品副标题')
    description = models.TextField(blank=True, null=True, db_comment='商品详情描述')
    price = models.DecimalField(max_digits=12, decimal_places=2, db_comment='售价')
    original_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, db_comment='原价')
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, db_comment='成本价')
    stock = models.PositiveIntegerField(blank=True, null=True, db_comment='库存数量')
    min_stock = models.PositiveIntegerField(blank=True, null=True, db_comment='最低库存预警')
    weight = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True, db_comment='商品重量（kg）')
    thumbnail = models.CharField(max_length=500, blank=True, null=True, db_comment='缩略图URL')
    gallery = models.TextField(blank=True, null=True, db_comment='商品图片集（JSON格式）')
    status = models.CharField(max_length=12, blank=True, null=True, db_comment='商品状态')
    sales_count = models.PositiveIntegerField(blank=True, null=True, db_comment='销售数量')
    view_count = models.PositiveIntegerField(blank=True, null=True, db_comment='浏览次数')
    sort_order = models.IntegerField(blank=True, null=True, db_comment='排序')
    seo_title = models.CharField(max_length=200, blank=True, null=True, db_comment='SEO标题')
    seo_keywords = models.CharField(max_length=500, blank=True, null=True, db_comment='SEO关键词')
    seo_description = models.CharField(max_length=500, blank=True, null=True, db_comment='SEO描述')
    is_hot = models.IntegerField(blank=True, null=True, db_comment='是否热门商品')
    is_new = models.IntegerField(blank=True, null=True, db_comment='是否新品')
    is_recommend = models.IntegerField(blank=True, null=True, db_comment='是否推荐商品')
    is_deleted = models.IntegerField(blank=True, null=True, db_comment='是否删除')
    create_time = models.DateTimeField(blank=True, null=True, db_comment='创建时间')
    update_time = models.DateTimeField(blank=True, null=True, db_comment='更新时间')

    class Meta:
        managed = False
        db_table = 'product'
        db_table_comment = '商品信息表'


class Category(models.Model):
    parent_id = models.PositiveIntegerField(blank=True, null=True, db_comment='父分类ID，0表示顶级分类')
    name = models.CharField(max_length=50, db_comment='分类名称')
    sort_order = models.IntegerField(blank=True, null=True, db_comment='排序顺序')
    icon_url = models.CharField(max_length=500, blank=True, null=True, db_comment='分类图标URL')
    is_active = models.IntegerField(blank=True, null=True, db_comment='是否启用')
    is_deleted = models.IntegerField(blank=True, null=True, db_comment='是否删除')
    create_time = models.DateTimeField(blank=True, null=True, db_comment='创建时间')
    update_time = models.DateTimeField(blank=True, null=True, db_comment='更新时间')

    class Meta:
        managed = False
        db_table = 'category'
        db_table_comment = '商品分类表'
