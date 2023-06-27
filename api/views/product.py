from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.models import Category, CategoryLevel, Product, ProductImage, ProductVariant
from api.serializers import ProductDetailSerializer, ProductSerializer
from api.utils.split_string import splitString


class ProductPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [filters.OrderingFilter,
                       filters.SearchFilter, DjangoFilterBackend]
    ordering_fields = ['price', 'lastUpdate']
    filterset_fields = [
        'isNew', 'subcategoryId', 'categoryId', 'priceGroup'
    ]
    ordering = ['-lastUpdate']
    search_fields = [
        'article', 'productName', 'description',
        'keywords', 'brand__name', 'brand__keywords'
    ]

    def get_queryset(self):
        items = Product.objects.select_related(
            'brand').filter(isAvailable=True, checked=True)

        items = self.filter_queryset(items)
        withImages = ProductImage.objects.values_list('imageId', flat=True)
        items = items.filter(productId__in=withImages)

        productIds = self.request.GET.get('productId')
        gender = self.request.GET.get('gender')
        brandIds = self.request.GET.get('brandIds')
        sizes = self.request.GET.get('sizes')

        if brandIds:
            brandIds = splitString(brandIds)
            items = items.filter(brand__brandId__in=brandIds)

        if gender == 'men' or gender == 'women':
            categoryIdsByGender = Category.objects.filter(
                level=CategoryLevel.CATEGORY,
                gender=gender
            ).values_list('categoryId', flat=True)
            categoryIdsByGender = [str(catId) for catId in categoryIdsByGender]
            items = items.filter(categoryId__in=categoryIdsByGender)
        if sizes:
            items = items.filter(
                productvariant__size__in=splitString(sizes)).distinct()
        # Фильтруем по значениям `productId`
        if productIds:
            items = items.filter(productId__in=splitString(productIds))

        availableSizes = ProductVariant.objects.filter(
            product__in=items).values_list('size', flat=True).distinct()
        return {
            'page': self.paginate_queryset(items),
            'sizes': availableSizes,
            'count': items.count()
        }

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset['page'], many=True)
        return Response({
            'count': queryset['count'],
            'products': serializer.data,
            'filters': {
                'sizes': queryset['sizes']
            }
        })


class ProductDetailView(RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()
    lookup_field = 'productId'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        variants = ProductVariant.objects.filter(product=instance)

        # Получаем соответствующие картинки для каждого идентификатора
        images = ProductImage.objects.filter(imageId=instance.productId)

        # Добавляем картинки в сериализатор товара
        instance.images = sorted(
            images, key=lambda image: image.priority
        )
        instance.variants = variants

        return Response(self.get_serializer(instance).data)
