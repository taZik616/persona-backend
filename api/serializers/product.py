from rest_framework import serializers

from api.models import Product, ProductImage, ProductVariant
from api.serializers import BrandSerializer


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('priority', 'compressedImage', 'originalImage')


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('productId', 'productName', 'price',
                  'priceGroup', 'collection', 'brand', 'images', 'onlyOneVariant')


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ('size', 'color', 'uniqueId', 'price', 'isAvailable')


class ProductDetailSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            'productId', 'productName', 'price', 'onlyOneVariant',
            'priceGroup', 'collection', 'brand', 'images', 'variants',
            'manufacturer', 'country', 'podklad', 'sostav', 'isAvailable'
        )
