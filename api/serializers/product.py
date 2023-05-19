from rest_framework import serializers

from api.models import Product, ProductImage, ProductVariant, Color
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

    def to_representation(self, instance):
        imageIds = instance.productId

        images = ProductImage.objects.filter(imageId=imageIds)

        instance.images = sorted(
            images,
            key=lambda image: image.priority
        )
        representation = super().to_representation(instance)
        return representation


class ProductVariantSerializer(serializers.ModelSerializer):
    colorHex = serializers.SerializerMethodField()

    def get_colorHex(self, instance):
        colorObj = Color.objects.filter(name=instance.color).first()
        if colorObj:
            return colorObj.hex
        else:
            return ''

    class Meta:
        model = ProductVariant
        fields = (
            'size', 'color', 'colorHex',
            'uniqueId', 'price', 'isAvailable'
        )


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
