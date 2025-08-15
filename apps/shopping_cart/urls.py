from django.urls import path
from .views import ShoppingCartAPIView


urlpatterns = [
    path("", ShoppingCartAPIView.as_view(), name="shopping_cart"),
]
