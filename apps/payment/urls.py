from django.urls import path
from apps.payment.views import (
    AlipayCreatePaymentAPIView,
    AlipayReturnAPIView,
    AlipayNotifyAPIView,
    PaymentStatusAPIView,
)

urlpatterns = [
    path('alipay/create/', AlipayCreatePaymentAPIView.as_view(), name='alipay-create'),
    path('alipay/return/', AlipayReturnAPIView.as_view(), name='alipay-return'),  # 同步回跳（GET）
    path('alipay/notify/', AlipayNotifyAPIView.as_view(), name='alipay-notify'),  # 异步通知（POST）
    path('status/', PaymentStatusAPIView.as_view(), name='payment-status'),
]

