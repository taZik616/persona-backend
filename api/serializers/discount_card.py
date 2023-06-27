from rest_framework import serializers

from api.models import DiscountCard, DiscountCardLevel


class DiscountCardLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCardLevel
        fields = ['level', 'discountPercent']


class DiscountCardSerializer(serializers.ModelSerializer):
    cardLevel = DiscountCardLevelSerializer()

    class Meta:
        model = DiscountCard
        fields = ['cardCode', 'cardLevel', 'purchaseTotal']
