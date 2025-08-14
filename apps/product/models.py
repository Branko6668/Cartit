from django.db import models


class ProductTag(models.Model):
    name = models.CharField(max_length=50, verbose_name='标签名称')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='标签标识')
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='标签描述')
    icon_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='标签图标URL')
    sort_order = models.IntegerField(default=0, verbose_name='排序权重')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_tag'
        verbose_name = '商品标签'
        verbose_name_plural = '商品标签'
        ordering = ['-sort_order', 'id']

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='商品ID')
    category = models.ForeignKey(
        'product.Category',
        on_delete=models.PROTECT,
        db_column='category_id',
        verbose_name='分类ID'
    )
    store = models.ForeignKey(
        'store.Store',
        on_delete=models.CASCADE,
        db_column='store_id',
        verbose_name='店铺ID'
    )
    name = models.CharField(max_length=200, verbose_name='商品名称')
    subtitle = models.CharField(max_length=500, blank=True, null=True, verbose_name='商品副标题')
    description = models.TextField(blank=True, null=True, verbose_name='商品详情描述')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='售价')
    original_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='原价')
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='成本价')
    stock = models.PositiveIntegerField(default=0, verbose_name='库存数量')
    min_stock = models.PositiveIntegerField(default=0, verbose_name='最低库存预警')
    weight = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True, verbose_name='商品重量（kg）')
    thumbnail = models.CharField(max_length=500, blank=True, null=True, verbose_name='缩略图URL')
    gallery = models.TextField(blank=True, null=True, verbose_name='商品图片集（JSON格式）')
    status = models.CharField(
        max_length=12,
        choices=[
            ('draft', '草稿'),
            ('on_sale', '在售'),
            ('off_sale', '下架'),
            ('out_of_stock', '缺货')
        ],
        default='draft',
        verbose_name='商品状态'
    )
    sales_count = models.PositiveIntegerField(default=0, verbose_name='销售数量')
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览次数')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name='SEO标题')
    seo_keywords = models.CharField(max_length=500, blank=True, null=True, verbose_name='SEO关键词')
    seo_description = models.CharField(max_length=500, blank=True, null=True, verbose_name='SEO描述')
    tags = models.ManyToManyField(ProductTag, related_name='products', blank=True, verbose_name='商品标签')
    # is_hot = models.BooleanField(default=False, verbose_name='是否热门商品')
    # is_new = models.BooleanField(default=False, verbose_name='是否新品')
    # is_recommend = models.BooleanField(default=False, verbose_name='是否推荐商品')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product'
        verbose_name = '商品信息'
        verbose_name_plural = '商品信息'
        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=0), name='chk_price'),
            models.CheckConstraint(check=models.Q(stock__gte=0), name='chk_stock')
        ]


class Category(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='分类ID')
    parent_id = models.PositiveIntegerField(default=0, verbose_name='父分类ID，0表示顶级分类')
    name = models.CharField(max_length=50, verbose_name='分类名称')
    sort_order = models.IntegerField(default=0, verbose_name='排序顺序')
    icon_url = models.CharField(max_length=500, blank=True, null=True, verbose_name='分类图标URL')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'category'
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'
