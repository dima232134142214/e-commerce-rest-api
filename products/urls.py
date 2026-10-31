

from django.urls import path
from .views import ProductListCreateView, ProductDetailView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("products/", ProductListCreateView.as_view(), name='product-list'),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
]