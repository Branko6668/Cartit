from django.urls import path
from .views import (
    ShoppingCartListCreateAPIView,
    ShoppingCartItemAPIView,
    ShoppingCartSelectAllAPIView,
    ShoppingCartClearAPIView,
)


urlpatterns = [
    path("", ShoppingCartListCreateAPIView.as_view(), name="shopping_cart_list_create"),
    path("item/<int:pk>/", ShoppingCartItemAPIView.as_view(), name="shopping_cart_item"),
    path("select_all", ShoppingCartSelectAllAPIView.as_view(), name="shopping_cart_select_all"),
    path("clear", ShoppingCartClearAPIView.as_view(), name="shopping_cart_clear"),
]
