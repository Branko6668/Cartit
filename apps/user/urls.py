from django.urls import path
from .views import UserAddressAPIView
from .views import UserRegisterAPIView
from .views import UserMeAPIView
from .views import UserAddressListAPIView
from .views import UserLoginAPIView, UserLogoutAPIView, UserUpdateAPIView, UserDeleteAPIView


urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="user"),
    path("login/", UserLoginAPIView.as_view(), name="user_login"),
    path("logout/", UserLogoutAPIView.as_view(), name="user_logout"),
    path("update/", UserUpdateAPIView.as_view(), name="user_update"),
    path("delete/", UserDeleteAPIView.as_view(), name="user_delete"),
    path("me/", UserMeAPIView.as_view(), name="user_me"),
    path("address/", UserAddressAPIView.as_view(), name="create_user_address"),
    path("address/<int:pk>/", UserAddressAPIView.as_view(), name="get_user_address"),
    path("address/list/", UserAddressListAPIView.as_view(), name="get_addresses"),
]