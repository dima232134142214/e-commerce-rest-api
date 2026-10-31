from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Ціна товару повинна бути більшою за нуль."
            )
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Кількість товару не може бути від'ємною."
                )
        return value
    
    class Meta:
        model = Product
        fields = '__all__'