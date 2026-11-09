from django.test import TestCase

# Create your tests here.
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from products.models import Product
from cart.models import Cart, CartItem
from .models import Order, OrderItem

User = get_user_model()


class CheckoutAPITestCase(APITestCase):
    
    def setUp(self):
        
        self.user = User.objects.create(
            username="testuser",
            password="testpassword123",
        )
        
        self.product = Product.objects.create(
            name="Test Keyboard",
            description="Test description",
            price=1500.00,
            stock=10,
            is_active=True,
        )
        
        self.cart = Cart.objects.create(user=self.user)
        
        self.client.force_authenticate(user=self.user)
        
    def test_checkout_success(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product, 
            quantity=2
        )
        
        response=self.client.post("/api/orders/checkout/")
        
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        
        order = Order.objects.get()
        
        self.assertEqual(order.total_price, Decimal("3000.00"))
        
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)
        
        self.assertEqual(CartItem.objects.count(), 0)
        
    def test_checkout_empty_cart(self):
        response = self.client.post("/api/orders/checkout/")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,)
        
        self.assertEqual(Order.objects.count(), 0)
        
    def test_checkout_insufficient_stock(self):
        CartItem.objects.create( 
            cart=self.cart,
            product=self.product,
            quantity=11,
            )
        
        response = self.client.post("/api/orders/checkout/")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.assertEqual(Order.objects.count(), 0)
        self.product.refresh_from_db
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(CartItem.objects.count(), 1)
        
    def test_checkout_unauthorized(self):
        self.client.force_authenticate(user=None)
        
        response = self.client.post("/api/orders/checkout/")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    