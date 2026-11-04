from django.urls import path

from .views import CartView, CartItemAddView


urlpatterns = [
    path("", CartView.as_view(), name="cart-detail"),
    path("items/", CartItemAddView.as_view(), name="cart-item-add")
]
