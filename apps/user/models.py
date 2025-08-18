from django.db import models

class User(models.Model):
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
    ]

    STATUS_CHOICES = [
        ('active', '正常'),
        ('disabled', '禁用'),
    ]

    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name='真实姓名')
    phone = models.CharField(max_length=11, unique=True, blank=True, null=True, verbose_name='手机号')
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True, verbose_name='邮箱')
    password = models.CharField(max_length=255, verbose_name='密码')
    avatar_url = models.CharField(max_length=500, blank=True, null=True, verbose_name='头像URL')
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default='other', verbose_name='性别')
    birthday = models.DateField(blank=True, null=True, verbose_name='生日')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active', verbose_name='账户状态')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'


class UserAddress(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    recipient_name = models.CharField(max_length=50, verbose_name='收件人姓名')
    recipient_phone = models.CharField(max_length=11, verbose_name='收件人电话')
    province = models.CharField(max_length=20, verbose_name='省份')
    city = models.CharField(max_length=20, verbose_name='城市')
    district = models.CharField(max_length=20, verbose_name='区县')
    detail_address = models.CharField(max_length=200, verbose_name='详细地址')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='邮政编码')
    is_default = models.BooleanField(default=False, verbose_name='是否默认地址')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'user_address'
        verbose_name = '用户地址'
        verbose_name_plural = '用户地址'
