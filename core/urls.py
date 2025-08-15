"""
core 项目的 URL 配置。

`urlpatterns` 列表用于将 URL 路由到视图。更多信息请参见：
    https://docs.djangoproject.com/zh/4.2/topics/http/urls/
示例：
函数视图
    1. 添加导入：from my_app import views
    2. 在 urlpatterns 中添加 URL：path('', views.home, name='home')
类视图
    1. 添加导入：from other_app.views import Home
    2. 在 urlpatterns 中添加 URL：path('', Home.as_view(), name='home')
包含其他 URLconf
    1. 导入 include() 函数：from django.urls import include, path
    2. 在 urlpatterns 中添加 URL：path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("product/", include("apps.product.urls")),
    path("shopping_cart/", include("apps.shopping_cart.urls"))
]
