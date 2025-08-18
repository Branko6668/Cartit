from django.urls import path
from apps.order.views import OrderCreateAPIView, DirectOrderCreateAPIView

urlpatterns = [
    path("create/", OrderCreateAPIView.as_view(), name="order-create"),
    path("direct/", DirectOrderCreateAPIView.as_view(), name="order-direct-create")
]