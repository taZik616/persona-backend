from rest_framework import serializers

from api.models import GiftCard, GiftCardType


class GiftCardTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCardType
        fields = '__all__'


class GiftCardSerializer(serializers.ModelSerializer):
    cardType = GiftCardTypeSerializer()

    class Meta:
        model = GiftCard
        fields = ('balance', 'cardType', 'promocode', 'isActive')
