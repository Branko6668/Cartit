from rest_framework.views import APIView
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponse
from apps.payment.alipay import Alpay
from apps.order.models import OrderInfo
from apps.payment.models import Payment
from utils.renderer import CustomResponse
from utils.error_codes import Codes
import uuid


def _get_user_id(request: Request):
    payload = getattr(request, 'auth', None)
    if isinstance(payload, dict):
        return payload.get('user_id')
    return None

class AlipayCreatePaymentAPIView(APIView):
    """创建支付宝支付链接
    POST /payment/alipay/create/
    请求: {"order_id": 123}
    返回: {"pay_url": "https://...", "payment_no": "PAY2024..."}
    仅允许订单状态为 pending_payment
    """
    def post(self, request: Request):
        uid = _get_user_id(request)
        if not uid:
            return CustomResponse(code=Codes.UNAUTHORIZED, msg='未登录', status=401)
        order_id = request.data.get('order_id')
        if not order_id:
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='缺少订单ID', errors={'order_id': 'required'}, status=400)
        try:
            order_id = int(order_id)
        except (TypeError, ValueError):
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='订单ID格式错误', errors={'order_id': 'int'}, status=400)
        order = get_object_or_404(OrderInfo, id=order_id, user_id=uid)
        if order.status != 'pending_payment':
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='订单状态不允许支付', errors={'status': order.status}, status=400)
        # 已存在未完成支付记录则复用
        payment = Payment.objects.filter(order=order, status='pending', payment_method='alipay').first()
        if not payment:
            payment_no = 'PAY' + timezone.now().strftime('%Y%m%d%H%M%S') + f"{order.id:06d}" + uuid.uuid4().hex[:4].upper()
            payment = Payment.objects.create(
                payment_no=payment_no,
                order=order,
                user_id=uid,
                amount=order.actual_amount,
                payment_method='alipay',
                payment_channel='alipay_page',
                status='pending'
            )
        alipay = Alpay()
        pay_url = alipay.direct_pay(
            subject=f"订单{order.order_no}",
            out_trade_no=payment.payment_no,
            total_amount=str(payment.amount)
        )
        return CustomResponse(code=Codes.USER_ACTION_OK, msg='创建支付链接成功', data={'pay_url': pay_url, 'payment_no': payment.payment_no}, status=200)

class AlipayReturnAPIView(APIView):
    """同步回跳(前端浏览器 GET)。仅做签名验证与结果提示，最终仍以异步通知为准。"""
    def get(self, request: Request):
        params = request.query_params.dict()
        if not params:
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='缺少参数', status=400)
        alipay = Alpay()
        valid = alipay.verify(params.copy())
        payment_no = params.get('out_trade_no')
        trade_no = params.get('trade_no')
        result = {
            'payment_no': payment_no,
            'trade_no': trade_no,
            'verified': bool(valid)
        }
        return CustomResponse(code=Codes.USER_ACTION_OK, msg='回跳已接收(最终结果以异步通知为准)', data=result, status=200)

class AlipayNotifyAPIView(APIView):
    """异步通知(服务器 POST)。需返回 'success' 字符串给支付宝。"""
    authentication_classes = []  # 支付宝回调不带用户身份
    permission_classes = []

    def post(self, request: Request):
        # 支付宝可能用 form 方式提交
        params = request.POST.dict() or (request.data if isinstance(request.data, dict) else {})
        params = dict(params)
        alipay = Alpay()
        verify_ok = alipay.verify(params.copy())
        if not verify_ok:
            return HttpResponse('fail')
        trade_status = params.get('trade_status')
        payment_no = params.get('out_trade_no')
        trade_no = params.get('trade_no')
        if not payment_no:
            return HttpResponse('fail')
        payment = Payment.objects.filter(payment_no=payment_no).select_related('order').first()
        if not payment:
            return HttpResponse('fail')
        # 幂等处理
        if payment.status == 'success':
            return HttpResponse('success')
        if trade_status in ('TRADE_SUCCESS', 'TRADE_FINISHED'):
            with transaction.atomic():
                payment.status = 'success'
                payment.transaction_id = trade_no
                now = timezone.now()
                payment.paid_time = now
                payment.notify_time = now
                payment.save(update_fields=['status', 'transaction_id', 'paid_time', 'notify_time'])
                order = payment.order
                if order.status == 'pending_payment':
                    order.status = 'paid'
                    order.payment_method = 'alipay'
                    order.payment_time = now
                    order.save(update_fields=['status', 'payment_method', 'payment_time'])
        else:
            # 其它状态可按需扩展 failed 等
            pass
        return HttpResponse('success')

class PaymentStatusAPIView(APIView):
    """查询支付状态
    GET /payment/status/?payment_no=xxx 或 ?order_id=123
    返回: {status: pending|success|failed|cancelled, payment_no, order_status}
    """
    def get(self, request: Request):
        uid = _get_user_id(request)
        if not uid:
            return CustomResponse(code=Codes.UNAUTHORIZED, msg='未登录', status=401)
        payment_no = request.query_params.get('payment_no')
        order_id = request.query_params.get('order_id')
        payment = None
        if payment_no:
            payment = Payment.objects.filter(payment_no=payment_no, user_id=uid).select_related('order').first()
        elif order_id:
            try:
                order_id_int = int(order_id)
            except (TypeError, ValueError):
                return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='order_id格式错误', errors={'order_id': 'int'}, status=400)
            payment = Payment.objects.filter(order_id=order_id_int, user_id=uid).order_by('-id').select_related('order').first()
        else:
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='缺少 payment_no 或 order_id', errors={'payment_no': 'optional', 'order_id': 'optional'}, status=400)
        if not payment:
            return CustomResponse(code=Codes.USER_PARAM_INVALID, msg='支付记录不存在', status=404)
        data = {
            'payment_no': payment.payment_no,
            'status': payment.status,
            'order_id': payment.order_id,
            'order_status': payment.order.status,
            'amount': str(payment.amount),
            'paid_time': payment.paid_time.isoformat() if payment.paid_time else None
        }
        return CustomResponse(code=Codes.USER_ACTION_OK, msg='查询成功', data=data, status=200)
