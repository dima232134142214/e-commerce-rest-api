

from django.urls import path
from .views import ProductListCreateView, ProductDetailView, RegistrationView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("products/", ProductListCreateView.as_view(), name='product-list'),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
]