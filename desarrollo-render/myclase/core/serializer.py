from rest_framework import serializers
from market.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "description", "marca", "price", "stock", "active", "created_at"]
