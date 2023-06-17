from rest_framework import serializers

from api.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['orderId', 'orderSberId', 'status', 'address', 'productsInfo', 'status']
