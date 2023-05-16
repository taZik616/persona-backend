from rest_framework import serializers

from api.models import Product, ProductImage
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
