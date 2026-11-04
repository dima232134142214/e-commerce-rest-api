

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from django.shortcuts import get_object_or_404


class CartView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        
        cart, created = Cart.objects.get_or_create(
            user=request.user
        )
        
        serializer = CartSerializer(cart)
        
        return Response(serializer.data)
    
class CartItemAddView(APIView):
    
    premission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer=CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product=serializer.validated_data['product']
        quantity=serializer.validated_data['quantity']
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        existing_item=CartItem.objects.filter(
            cart=cart,
            product=product,
        ).first()
        
        current_quantity=existing_item.quantity if existing_item else 0
        new_quantity= current_quantity + quantity
        
        
        if new_quantity > product.stock:
            return Response(
                {
                    "error": f"Available stock: {product.stock - current_quantity}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if existing_item:
            existing_item.quantity = new_quantity
            existing_item.save(update_fields=["quantity", "updated_at"])
            cart_item = existing_item
        else:
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity,
            )
            
        return Response(
            CartItemSerializer(cart_item).data,
            status=status.HTTP_201_CREATED,
        )

class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    
    def patch(self, request, pk):
        
        cart_item = get_object_or_404(
            CartItem,
            pk=pk,
            cart__user=request.user,
        )
        
        serializer = CartItemSerializer(
            cart_item,
            data=request.data,
            partial=True,
        )
        
        serializer.is_valid(raise_exception=True)
        
        new_quantity = serializer.validated_data.get(
            "quantity",
            cart_item.quantity,
        )
        
        if new_quantity > cart_item.product.stock:
            return Response(
                {
                    "error": f"Available stock: {cart_item.product.stock}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item.quantity = new_quantity
        cart_item.save(update_fields=["quantity", "updated_at"])
        
        return Response(
            CartItemSerializer(cart_item).data,
            status=status.HTTP_200_OK,
        )