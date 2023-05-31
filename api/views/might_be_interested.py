from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from api.models import Product, ProductImage
from api.serializers import ProductSerializer
from itertools import chain
import random

class MightBeInterestedView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        items = Product.objects.select_related('brand').filter(isAvailable=True)

        brandId = self.request.GET.get('brandId')
        categoryId = self.request.GET.get('categoryId')
        excludeProductId = self.request.GET.get('exclude')
        subcategoryId = self.request.GET.get('subcategoryId')
        collection = self.request.GET.get('collection')
        brandId = self.request.GET.get('brandId')

        withImages = ProductImage.objects.values_list('imageId', flat=True)
        items = items.filter(productId__in=withImages)

        sameBrand = items.order_by('?').filter(
            brand__brandId=brandId
        )[:10] if brandId else []
        sameCategory = items.order_by('?').filter(
            categoryId=categoryId
        )[:10] if categoryId else []
        sameSubcategory = items.order_by('?').filter(
            subcategoryId=subcategoryId
        )[:10] if subcategoryId else []
        sameCollection = items.order_by('?').filter(
            collection=collection
        )[:10] if collection else []

        items = list(chain(sameBrand, sameCategory, sameSubcategory, sameCollection))
        unique_items = []
        added_product_ids = set(excludeProductId) if excludeProductId else set()

        for item in items:
            if item.productId not in added_product_ids:
                unique_items.append(item)
                added_product_ids.add(item.productId)
        random.shuffle(unique_items)
        

        return self.filter_queryset(items)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
