from django.test import TestCase

# Create your tests here.
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from .models import Product

User = get_user_model()

class ProductAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="testadmin",
            email="testadmin@example.com",
            password="TestPassword123!",
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="TestPassword123!",
            )
        
        self.product = Product.objects.create(
            name="Test Phone",
            description="Test description",
            price="999.99",
            stock=10,
        )
        
    def authenticate_with_jwt(self, user):
        response = self.client.post(
            "/api/token/",
            {
                "username": user.username,
                "password": "TestPassword123!",
                },
            format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data["access"]
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
            )

    def test_get_products(self):
        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        
    def test_create_product(self):
        
        self.authenticate_with_jwt(self.admin)
        
        data = {
            "name": "Laptop",
            "description": "Test laptop",
            "price": "25000.00",
            "stock": 5,
            "is_active": True,
        }

        response = self.client.post("/api/products/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Product.objects.filter(name="Laptop").exists()
        )

    def test_reject_negative_price(self):
        
        self.authenticate_with_jwt(self.admin)
        
        data = {
            "name": "Invalid Product",
            "description": "Invalid price",
            "price": "-100.00",
            "stock": 5,
            "is_active": True,
        }

        response = self.client.post("/api/products/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)
        
    def test_update_product(self):
        
        self.authenticate_with_jwt(self.admin)

        
        data = {
            "name": "Updated Phone",
            "description": "Updated description",
            "price": "1299.99",
            "stock": 15,
            "is_active": True,
            }
        response = self.client.patch(
            f"/api/products/{self.product.pk}/",
            data,
            format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Phone")

    def test_delete_product(self):
        
        self.authenticate_with_jwt(self.admin)
        
        response = self.client.delete(
            f"/api/products/{self.product.pk}/"
            )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Product.objects.filter(pk=self.product.pk).exists()
            )
    
    def test_create_product_forbidden_for_anonymous(self):
        response = self.client.post(
            "/api/products/",
            {
                "name": "Unauthorized Product",
                "description": "Should not be created",
                "price": "100.00",
                "stock": 5,
                },
            format="json",
            )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            )
    
    def test_update_product_forbidden_for_anonymous(self):
        response = self.client.patch(
            f"/api/products/{self.product.pk}/",
            {"name": "Unauthorized Update"},
            format="json",
            )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            )
    
    def test_delete_product_forbidden_for_anonymous(self):
        response = self.client.delete(
            f"/api/products/{self.product.pk}/"
            )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            )
        
    def test_create_product_forbidden_for_regular_user(self):
        self.authenticate_with_jwt(self.user)
        response = self.client.post(
            "/api/products/",
            {
                "name": "Unauthorized Product",
                "description": "Regular user cannot create products",
                "price": "100.00",
                "stock": 5,
                },
            format="json",
            )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            )
    
    def test_update_product_forbidden_for_regular_user(self):
        self.authenticate_with_jwt(self.user)
        response = self.client.patch(
            f"/api/products/{self.product.pk}/",
            {"name": "Unauthorized Update"},
            format="json",
            )
        
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            )
        
    def test_delete_product_forbidden_for_regular_user(self):
        self.authenticate_with_jwt(self.user)
        response = self.client.delete(
            f"/api/products/{self.product.pk}/"
            )
        
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            )
    
    def test_obtain_token_with_invalid_password(self):
        response = self.client.post(
            "/api/token/",
            {
                "username": self.admin.username,
                "password": "WrongPassword123!",
                },
            format="json",
            )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            )
    
    def test_create_product_with_invalid_token(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer invalid.token.value"
            )
        
        response = self.client.post(
            "/api/products/",
            {
                "name": "Invalid Token Product",
                "description": "Should not be created",
                "price": "100.00",
                "stock": 5,
                },
            format="json",
            )
        
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            )
        
    def test_obtain_token_with_valid_credentials(self):
        response = self.client.post(
            "/api/token/",
            {
                "username": self.admin.username,
                "password": "TestPassword123!",
                },
            format="json",
            )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            )
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        
    def test_refresh_access_token(self):
        token_response = self.client.post(
            "/api/token/",
            {
                "username": self.admin.username,
                "password": "TestPassword123!",
                },
            format="json",
            )
        refresh_token = token_response.data["refresh"]
        response = self.client.post(
            "/api/token/refresh/",
            {"refresh": refresh_token},
            format="json",
            )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            )
        self.assertIn("access", response.data)
        
    def test_refresh_with_invalid_token(self):
        response = self.client.post(
            "/api/token/refresh/",
            {"refresh": "invalid.refresh.token"},
            format="json",
            )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            )
    
    def test_filter_products_by_min_price(self):
        response = self.client.get(
            "/api/products/?min_price=1000"
            )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for product in response.data["results"]:
            self.assertGreaterEqual(
                product["price"],
                "1000.00",
                )
    
    
    def test_search_products_by_name(self):
        response = self.client.get(
            "/api/products/?search=Test Phone"
            )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertTrue(
            any(
                product["name"] == "Test Phone"
                for product in response.data["results"]
                )
            )
        
        
    def test_order_products_by_price(self):
        Product.objects.create(
            name="Cheap Product",
            description="Cheap test product",
            price="100.00",
            stock=10,
            )
            
        response = self.client.get(
            "/api/products/?ordering=price"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        prices = [product["price"] for product in response.data["results"]]
        self.assertEqual(prices, sorted(prices, key=lambda price: float(price)))
        
    def test_products_pagination(self):
        Product.objects.bulk_create([
            Product(
                name=f"Product {number}",
                description="Pagination test",
                price="100.00",
                stock=5,
                )
            for number in range(12)
            ])
        response = self.client.get("/api/products/")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            )
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 13)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])


    



