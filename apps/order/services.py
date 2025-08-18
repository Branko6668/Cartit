from collections import defaultdict
from typing import List
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from apps.shopping_cart.models import ShoppingCart
from apps.order.models import OrderInfo, OrderItem
from apps.product.models import Product

def _gen_order_no() -> str:
    return timezone.now().strftime("%Y%m%d%H%M%S%f")

@transaction.atomic
def create_orders_from_cart(*, user_id: int, recipient: dict, remark: str = "") -> List[OrderInfo]:
    cart_qs = ShoppingCart.objects.select_related("product").filter(user_id=user_id, selected=True)
    cart_items = list(cart_qs)
    if not cart_items:
        raise ValueError("购物车为空")

    product_ids = [ci.product_id for ci in cart_items]
    products = {p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)}

    store_groups = defaultdict(list)
    for ci in cart_items:
        p = products.get(ci.product_id)
        if not p:
            raise ValueError(f"商品不存在: {ci.product_id}")
        if ci.quantity <= 0:
            raise ValueError("非法数量")
        store_groups[p.store_id].append((ci, p))

    orders = []
    now = timezone.now()

    for store_id, items in store_groups.items():
        total_amount = Decimal("0.00")
        discount_amount = Decimal("0.00")
        freight_amount = Decimal("0.00")
        order_items = []

        for ci, p in items:
            price = Decimal(p.price)
            line_total = price * ci.quantity
            total_amount += line_total

            order_items.append(OrderItem(
                product_id=p.id,
                product_name=p.name,
                product_image=getattr(p, "image", "") or "",
                price=price,
                quantity=ci.quantity,
                total_amount=line_total,
                create_time=now,
            ))

            # 扣减库存
            p.stock -= ci.quantity
            p.save(update_fields=["stock"])

        actual_amount = total_amount - discount_amount + freight_amount
        if actual_amount < 0:
            actual_amount = Decimal("0.00")

        order = OrderInfo.objects.create(
            order_no=_gen_order_no(),
            total_amount=total_amount,
            discount_amount=discount_amount,
            freight_amount=freight_amount,
            actual_amount=actual_amount,
            status="pending_payment",
            payment_method=None,
            payment_time=None,
            ship_time=None,
            deliver_time=None,
            recipient_name=recipient["name"],
            recipient_phone=recipient["phone"],
            recipient_address=recipient["address"],
            remark=remark,
            store_id=store_id,
            user_id=user_id,
            create_time=now,
            update_time=now,
        )

        for oi in order_items:
            oi.order_id = order.id
        OrderItem.objects.bulk_create(order_items, batch_size=500)

        orders.append(order)

    cart_qs.delete()
    return orders

@transaction.atomic
def create_order_direct(user_id: int, product_id: int, quantity: int, recipient: dict, remark: str = "") -> OrderInfo:
    if quantity <= 0:
        raise ValueError("购买数量必须大于0")

    try:
        product = Product.objects.select_for_update().get(id=product_id)
    except Product.DoesNotExist:
        raise ValueError("商品不存在")

    if product.stock < quantity:
        raise ValueError("库存不足")

    now = timezone.now()
    price = Decimal(product.price)
    total_amount = price * quantity
    discount_amount = Decimal("0.00")
    freight_amount = Decimal("0.00")
    actual_amount = total_amount - discount_amount + freight_amount
    if actual_amount < 0:
        actual_amount = Decimal("0.00")

    order = OrderInfo.objects.create(
        order_no=_gen_order_no(),
        user_id=user_id,
        store_id=product.store_id,
        total_amount=total_amount,
        discount_amount=discount_amount,
        freight_amount=freight_amount,
        actual_amount=actual_amount,
        status="pending_payment",
        payment_method=None,
        payment_time=None,
        ship_time=None,
        deliver_time=None,
        recipient_name=recipient["name"],
        recipient_phone=recipient["phone"],
        recipient_address=recipient["address"],
        remark=remark,
        create_time=now,
        update_time=now,
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        product_name=product.name,
        product_image=getattr(product, "image", "") or "",
        price=price,
        quantity=quantity,
        total_amount=total_amount,
        create_time=now,
    )

    product.stock -= quantity
    product.save(update_fields=["stock"])

    return order