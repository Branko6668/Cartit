from django.urls import path
from .views import (
    UserRegisterAPIView,
    UserMeAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserUpdateAPIView,
    UserDeleteAPIView,
    UserAddressCreateAPIView,
    UserAddressDetailAPIView,
    UserAddressListAPIView,
)


urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="user_register"),
    path("login/", UserLoginAPIView.as_view(), name="user_login"),
    path("logout/", UserLogoutAPIView.as_view(), name="user_logout"),
    path("update/", UserUpdateAPIView.as_view(), name="user_update"),
    path("delete/", UserDeleteAPIView.as_view(), name="user_delete"),
    path("me/", UserMeAPIView.as_view(), name="user_me"),

    # 地址：创建/详情/列表
    path("address/", UserAddressCreateAPIView.as_view(), name="user_address_create"),  # POST only
    path("address/<int:pk>/", UserAddressDetailAPIView.as_view(), name="user_address_detail"),  # GET/PUT/DELETE
    path("address/list/", UserAddressListAPIView.as_view(), name="user_address_list"),  # GET
]