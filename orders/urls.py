from django.urls import path

from .views import (
    CheckoutView,
    OrderListView,
    OrderDetailView,
    OrderCancelView
)

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name='checkout'),
    path("", OrderListView.as_view(), name="order-list"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path('<int:pk>/cancel/', OrderCancelView.as_view(), name="order-cancel",)
]
