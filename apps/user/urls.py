from django.urls import path
from .views import UserRegisterAPIView, UserMeAPIView
# from .views import UserLoginAPIView, UserLogoutAPIView, UserUpdateAPIView, UserDelete

urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="user"),
    # path("login/", UserLoginAPIView.as_view(), name="user_login"),
    # path("logout/", UserLogoutAPIView.as_view(), name="user_logout"),
    # path("update/", UserUpdateAPIView.as_view(), name="user_update"),
    # path("delete/", UserDeleteAPIView.as_view(), name="user_delete"),
    path("me/", UserMeAPIView.as_view(), name="user_me"),
]