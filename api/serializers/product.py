from rest_framework import serializers

from api.models import Product, ProductImage, ProductVariant, Color, Category, CategoryLevel
from api.serializers import BrandSerializer


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('priority', 'compressedImage', 'originalImage')


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    images = ProductImageSerializer(many=True, read_only=True)
    gender = serializers.SerializerMethodField()

    def get_gender(self, instance):
        gender = Category.objects.filter(
            level=CategoryLevel.CATEGORY,
            categoryId=instance.categoryId
        ).first().gender
        return gender if gender  else ''

    class Meta:
        model = Product
        fields = ('productId', 'productName', 'price', 'isAvailable', 'gender', 'discountPercent',
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
            return '#000000'

    class Meta:
        model = ProductVariant
        fields = (
            'size', 'color', 'colorHex',
            'uniqueId', 'price', 'isAvailable',
            'discountPercent'
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    gender = serializers.SerializerMethodField()

    def get_gender(self, instance):
        gender = Category.objects.filter(
            level=CategoryLevel.CATEGORY,
            categoryId=instance.categoryId
        ).first().gender
        return gender if gender  else ''

    class Meta:
        model = Product
        fields = (
            'productId', 'productName', 'price', 'priceGroup', 'gender',
            'onlyOneVariant', 'collection', 'isAvailable', 'description',
            'manufacturer', 'country', 'podklad', 'sostav', 
            'brand', 'images', 'variants', 'discountPercent'
        )
