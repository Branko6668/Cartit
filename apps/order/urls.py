from django.urls import path
from apps.order.views import (
    OrderCreateAPIView,
    DirectOrderCreateAPIView,
    OrderListAPIView,
    OrderDetailAPIView,
)

urlpatterns = [
    path("create/", OrderCreateAPIView.as_view(), name="order-create"),
    path("direct/", DirectOrderCreateAPIView.as_view(), name="order-direct-create"),
    path("list/", OrderListAPIView.as_view(), name="order-list"),
    path("<int:pk>/", OrderDetailAPIView.as_view(), name="order-detail"),
]