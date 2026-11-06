from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers. ModelSerializer):
    
    product = ProductSerializer(read_only=True)
    
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
        write_only=True
    )
    
    quantity = serializers.IntegerField(min_value=1)
    
    class Meta:
        model=CartItem
        fields = [
            "id",
            "product",
            "product_id",
            "quantity",
            "created_at",
            "updated_at",
        ]
        
        read_only_fields = ["id", "created_at", "updated_at"]
        
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model=Cart
        fields = [
            "id",
            "items",
            "created_at",
            "updated_at",
        ]
        
        read_only_fields = ["id", "created_at", "updated_at"]