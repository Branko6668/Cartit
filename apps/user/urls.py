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
    UserSendCodeAPIView,
    UserResetPasswordAPIView,
    UserProfileAPIView,
    UserAddressSetDefaultAPIView,
    UserAvatarUploadAPIView,  # 新增
)


urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="user_register"),
    path("login/", UserLoginAPIView.as_view(), name="user_login"),
    path("logout/", UserLogoutAPIView.as_view(), name="user_logout"),
    path("update/", UserUpdateAPIView.as_view(), name="user_update"),
    path("delete/", UserDeleteAPIView.as_view(), name="user_delete"),
    path("me/", UserMeAPIView.as_view(), name="user_me"),
    path("profile/", UserProfileAPIView.as_view(), name="user_profile"),
    path("send_code/", UserSendCodeAPIView.as_view(), name="user_send_code"),
    path("reset_password/", UserResetPasswordAPIView.as_view(), name="user_reset_password"),

    # 地址：创建/详情/列表/设默认
    path("address/", UserAddressCreateAPIView.as_view(), name="user_address_create"),  # POST only
    path("address/<int:pk>/", UserAddressDetailAPIView.as_view(), name="user_address_detail"),  # GET/PUT/DELETE
    path("address/list/", UserAddressListAPIView.as_view(), name="user_address_list"),  # GET
    path("address/<int:pk>/default/", UserAddressSetDefaultAPIView.as_view(), name="user_address_set_default"),  # PUT

    # 头像上传
    path("avatar/", UserAvatarUploadAPIView.as_view(), name="user_avatar_upload"),
]