import random
from itertools import chain

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from api.models import Product, ProductImage
from api.serializers import ProductSerializer


class MightBeInterestedView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        items = Product.objects.select_related(
            'brand').filter(isAvailable=True)

        return self.filter_queryset(items)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        productId = self.request.GET.get('productId')
        if not productId:
            return Response({'error': 'Укажите идентификатор товара'}, status=400)
        product = queryset.filter(productId=productId).first()
        if not product:
            return Response({'error': 'Товар с данным id не был найден'}, status=400)

        brandId = product.brand.brandId if product.brand else ''
        categoryId = product.categoryId
        subcategoryId = product.subcategoryId
        collection = product.collection

        withImages = ProductImage.objects.values_list('imageId', flat=True)
        queryset = queryset.filter(productId__in=withImages)

        sameBrand = queryset.order_by('?').filter(
            brand__brandId=brandId
        )[:10] if brandId else []
        sameCategory = queryset.order_by('?').filter(
            categoryId=categoryId
        )[:10] if categoryId else []
        sameSubcategory = queryset.order_by('?').filter(
            subcategoryId=subcategoryId
        )[:10] if subcategoryId else []
        sameCollection = queryset.order_by('?').filter(
            collection=collection
        )[:10] if collection else []

        queryset = list(chain(sameBrand, sameCategory,
                        sameSubcategory, sameCollection))
        unique_items = []
        added_product_ids = set(productId) if productId else set()

        for item in queryset:
            if item.productId not in added_product_ids:
                unique_items.append(item)
                added_product_ids.add(item.productId)
        random.shuffle(unique_items)

        serializer = self.get_serializer(unique_items, many=True)
        return Response(serializer.data)
