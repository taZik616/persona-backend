from rest_framework import serializers

from api.models import Order


class OrderSerializer(serializers.ModelSerializer):
    totalSum = serializers.SerializerMethodField()

    def get_totalSum(self, instance: Order):
        # Ваша логика для получения URL изображения
        price = 0
        for el in instance.productsInfo:
            price += el['variant']['price'] - el['variant']['price'] / \
                100 * el['variant']['discountPercent']
            if el.get('personalDiscountInRub'):
                price -= el['personalDiscountInRub']
        return price

    class Meta:
        model = Order
        fields = ['orderId', 'orderSberId', 'status',
                  'address', 'totalSum', 'status', 'productsInfo']
