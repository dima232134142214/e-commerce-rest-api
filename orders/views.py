from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .services import create_order_from_cart, cancel_order
from .serializers import OrderSerializer
from rest_framework import generics

from .models import Order
from .serializers import OrderSerializer


class CheckoutView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        order = create_order_from_cart(request.user)
        
        serializer = OrderSerializer(order)
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

class OrderListView(generics.ListAPIView):
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user).prefetch_related("items__product").order_by("-created_at")
        )

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("items__product")
        )

class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        
        order = cancel_order(
            user=request.user,
            order_id=pk,
        )
        
        serializer = OrderSerializer(order)
        
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )