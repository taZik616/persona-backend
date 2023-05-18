from rest_framework import serializers

from ..models import User, BasketItem, FavoriteItem
from .product import ProductSerializer, ProductVariantSerializer


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = [
            'is_superuser', 'is_staff', 'password',
            'last_login', 'groups', 'user_permissions'
        ]

    def update(self, instance, validated_data):
        instance.language = validated_data.get('language', instance.language)
        instance.firstName = validated_data.get(
            'firstName', instance.firstName)
        instance.lastName = validated_data.get('lastName', instance.lastName)
        instance.email = validated_data.get('email', instance.email)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.subEmail = validated_data.get('subEmail', instance.subEmail)
        instance.subSms = validated_data.get('subSms', instance.subSms)
        instance.subPush = validated_data.get('subPush', instance.subPush)
        # instance.favorites = validated_data.get('favorites', instance.favorites)
        return instance


class BasketItemsSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    variant = ProductVariantSerializer()

    class Meta:
        model = BasketItem
        fields = ('product', 'variant')


class FavoriteItemsSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = FavoriteItem
        fields = ('product',)
