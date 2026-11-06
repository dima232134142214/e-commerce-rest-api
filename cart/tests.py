from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from rest_framework import status 

from django.contrib.auth import get_user_model 

from products.models import Product
from cart.models import Cart, CartItem

User = get_user_model()



class CartAPITestCase(APITestCase):
    
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
        
        self.client.force_authenticate(user=self.user)
        
    
    def test_get_cart(self):
        response = self.client.get("/api/cart/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("items", response.data)
        self.assertEqual(response.data["items"], [])
        
    def test_get_cart_unauthorized(self):
        self.client.force_authenticate(user=None)
        
        response = self.client.get("/api/cart/")
        
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        
    def test_add_item_to_cart(self):
        data = {
            "product_id": self.product.id,
            "quantity": 2,
        }
        
        response = self.client.post(
            "/api/cart/items/", 
            data, 
            format="json",
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,)
        self.assertEqual(response.data["quantity"], 2)
        self.assertEqual(CartItem.objects.count(), 1)
        
    
    def test_add_existing_item_increases_quantity(self):
        data = {
            "product_id": self.product.id,
            "quantity": 2,
        }
        
        self.client.post(
            "/api/cart/items/",
            data,
            format="json"
        )
        
        data = {
            "product_id": self.product.id,
            "quantity": 3,
        }
                
        response = self.client.post(
            "/api/cart/items/",
            data,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK,)
        self.assertEqual(response.data["quantity"], 5)
        self.assertEqual(CartItem.objects.count(), 1)
        
    
    def test_add_item_exceeds_stock(self):
        
        data = {
            "product_id": self.product.id,
            "quntity": 11,
        }
        
        response = self.client.post(
            "/api/cart/items/",
            data,
            format="json",
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CartItem.objects.count(), 0)
        
    
    def test_update_cart_item_quantity(self):
        cart = Cart.objects.create(user=self.user)
        
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2,
        )
        
        data = {
            "quantity": 5,
        }
        
        response = self.client.patch(
            f"/api/cart/items/{cart_item.id}/",
            data,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quantity"], 5)
        
        cart_item.refresh_from_db()
        
        self.assertEqual(cart_item.quantity, 5)
        
    
    def test_update_cart_item_exceeds_stock(self):
        cart = Cart.objects.create(user=self.user)
                
        cart_item = CartItem.objects.create(
                    cart=cart,
                    product=self.product,
                    quantity=2,
                )
                
        data = {
                    "quantity": 11,
                }
                
        response = self.client.patch(
                    f"/api/cart/items/{cart_item.id}/",
                    data,
                    format="json",
                )
                
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                
        cart_item.refresh_from_db()
                
        self.assertEqual(cart_item.quantity, 2)
        
    def test_delete_cart_item(self):
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2,
            )
        
        response = self.client.delete(
            f"/api/cart/items/{cart_item.id}/"
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
    
    def test_user_cannot_update_another_users_cart_item(self):
        other_user = User.objects.create_user(
            username="otheruser",
            password="testpassword123",
        )
        
        other_cart = Cart.objects.create(user=other_user)
        
        other_item = CartItem.objects.create(
            cart=other_cart,
            product=self.product,
            quantity=2,
        )
        
        response = self.client.patch(
            f"/api/cart/items/{other_item.id}/",
            {"quantity": 5},
            format="json",
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,)
        
        other_item.refresh_from_db()
        
        self.assertEqual(other_item.quantity, 2)
    
    def test_user_cannot_delete_another_users_cart_item(self):
        other_user = User.objects.create_user(
            username="otheruser",
            password="testpassword123",
            )
                
        other_cart = Cart.objects.create(user=other_user)
                
        other_item = CartItem.objects.create(
            cart=other_cart,
            product=self.product,
            quantity=2,
            )
                
        response = self.client.delete(
            f"/api/cart/items/{other_item.id}/",
            )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        self.assertTrue(CartItem.objects.filter(id=other_item.id).exists())