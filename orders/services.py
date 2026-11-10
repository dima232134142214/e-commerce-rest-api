

from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound

from cart.models import Cart, CartItem
from products.models import Product
from .models import Order, OrderItem


@transaction.atomic
def create_order_from_cart(user):
    try:
        cart = Cart.objects.select_for_update().get(user=user)
    except Cart.DoesNotExist:
        raise ValidationError("Cart is empty")
    
    cart_items = list(
        CartItem.objects.filter(cart=cart).select_related("product")
    )
    
    if not cart_items:
        raise ValidationError("Cart is empty")
    
    total_price = Decimal("0.00")
    order_items = []
    products_to_update = []
    
    for cart_item in cart_items:
        product = Product.objects.select_for_update().get(
            pk=cart_item.product.id
        )
        
        if cart_item.quantity > product.stock:
            raise ValidationError(
                f"Not enough stock for {product.name}. "
                f"Available stock: {product.stock}"
            )
        
        item_price = product.price
        total_price += item_price * cart_item.quantity
        
        order_items.append(
            OrderItem(
                product=product,
                quantity=cart_item.quantity,
                price=item_price,
            )
        )
        
        product.stock -= cart_item.quantity
        products_to_update.append(product)
    
    order = Order.objects.create(
        user=user,
        total_price=total_price,
    )
    
    for item in order_items:
        item.order = order
        
    OrderItem.objects.bulk_create(order_items)
    
    Product.objects.bulk_update(
        products_to_update,
        ["stock"],
    )
    
    CartItem.objects.filter(cart=cart).delete()
    
    return order

@transaction.atomic
def cancel_order(user, order_id):
    try:
        order = Order.objects.select_for_update().get(
            pk=order_id,
            user=user,
        )
    except Order.DoesNotExist:
        raise NotFound("Order not found.")
    
    if order.status != Order.Status.PENDING: 
        raise ValidationError("Only pending orders can be cancelled.") 
    
    order_items = order.items.order_by("product_id")
    
    for items in order_items:
        product = Product.objects.select_for_update().get(
            pk=items.product_id
        )
        
        product.stock += items.quantity
        product.save(update_fields=["stock"])
    
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status", "updated_at"])
    
    return order