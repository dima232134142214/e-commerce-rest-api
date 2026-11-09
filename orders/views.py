from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .services import create_order_from_cart
from .serializers import OrderSerializer


class CheckoutView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        order = create_order_from_cart(request.user)
        
        serializer = OrderSerializer
        
        return Response(
            serializer.data,
            status=status.HTTP_201.CREATED,
        )