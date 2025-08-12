from django.db import models

class Store(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='店铺ID')
    store_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='店铺名称'
    )
    owner = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        db_column='owner_id',
        verbose_name='店主用户ID'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='店铺描述'
    )
    logo_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='店铺Logo URL'
    )
    contact_phone = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name='联系电话'
    )
    business_license = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='营业执照号'
    )
    status = models.CharField(
        max_length=9,
        choices=[
            ('pending', '待审核'),
            ('active', '营业中'),
            ('suspended', '暂停营业'),
            ('closed', '已关闭')
        ],
        default='pending',
        verbose_name='店铺状态'
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='是否删除'
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    update_time = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'store'
        verbose_name = '店铺信息'
        verbose_name_plural = '店铺信息'
