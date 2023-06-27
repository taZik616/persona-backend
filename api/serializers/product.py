from rest_framework import serializers

from api.models import (Category, CategoryLevel, Collection, Color, Product,
                        ProductImage, ProductVariant)
from api.serializers.brand import BrandSerializer
from api.serializers.collection import CollectionSerializer
from api.utils import splitString


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('priority', 'compressedImage', 'originalImage')


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    images = ProductImageSerializer(many=True, read_only=True)
    gender = serializers.SerializerMethodField()
    collections = serializers.SerializerMethodField()

    def get_gender(self, instance):
        gender = Category.objects.filter(
            level=CategoryLevel.CATEGORY,
            categoryId=instance.categoryId
        ).first().gender
        return gender if gender else ''

    def get_collections(self, instance):
        collectionIds = splitString(instance.collection)
        collections = Collection.objects.filter(collectionId__in=collectionIds)

        return CollectionSerializer(collections, many=True).data

    class Meta:
        model = Product
        fields = (
            'productId', 'productName', 'price', 'isAvailable', 'gender', 'discountPercent',
            'priceGroup', 'collections', 'brand', 'images', 'onlyOneVariant', 'article'
        )

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
    collections = serializers.SerializerMethodField()

    def get_gender(self, instance):
        gender = Category.objects.filter(
            level=CategoryLevel.CATEGORY,
            categoryId=instance.categoryId
        ).first().gender
        return gender if gender else ''

    def get_collections(self, instance):
        collectionIds = splitString(instance.collection)
        collections = Collection.objects.filter(collectionId__in=collectionIds)

        return CollectionSerializer(collections, many=True).data

    class Meta:
        model = Product
        fields = (
            'productId', 'productName', 'price', 'priceGroup', 'gender',
            'onlyOneVariant', 'collections', 'isAvailable', 'description',
            'manufacturer', 'country', 'podklad', 'sostav',
            'brand', 'images', 'variants', 'discountPercent', 'article'
        )
