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
    def test_get_order_list(self):
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal("3000.00"),
            )
        
        response = self.client.get("/api/orders/")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], order.id)
        
    def test_user_cannot_view_another_users_order(self):
        other_user = User.objects.create_user(
            username="otheruser",
            password="testpassword123",
            )
        
        other_order = Order.objects.create(
            user=other_user,
            total_price=Decimal("1500.00"),
            )
        response = self.client.get(
            f"/api/orders/{other_order.id}/"
            )
        
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            )
    
    
    def test_get_order_detail(self):
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal("3000.00")
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=Decimal("1500.00"),
        )
        
        response = self.client.get(
            f"/api/orders/{order.id}/"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], order.id)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["quantity"], 2)
    
    def test_cancel_order_success(self):
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal("3000.00"),
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=Decimal("1500.00"),
            )
        
        self.product.stock = 8 
        self.product.save()
        
        response = self.client.post(f"/api/orders/{order.id}/cancel/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.product.refresh_from_db()
        
        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertEqual(self.product.stock, 10)
    
    
    def test_cancel_order_twice(self):
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal("3000.00"),
            status=Order.Status.CANCELLED,
        )
        
        response = self.client.post(f"/api/orders/{order.id}/cancel/")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,)
    
    
    def test_user_cannot_cancel_another_users_order(self):
        other_user = User.objects.create_user(
            username="otheruser",
            password="testpassword123",
        )
        
        order = Order.objects.create(
            user=other_user,
            total_price=Decimal("1500.00"),
        )
        
        response = self.client.post(f"/api/orders/{order.id}/cancel/")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,)
        