from api.utils.split_string import splitString
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from api.models import Product, ProductImage, ProductVariant, Category, CategoryLevel
from api.serializers import ProductSerializer, ProductDetailSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

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
        'isNew', 'subcategoryId', 'categoryId', 'priceGroup'  # 'productId',
    ]
    ordering = ['-lastUpdate']
    search_fields = [
        'productName', 'collection', 'description',
        'keywords', 'brand__name', 'brand__keywords'
    ]

    def get_queryset(self):
        items = Product.objects.select_related(
            'brand').filter(isAvailable=True)
        productIds = self.request.GET.get('productId')
        gender = self.request.GET.get('gender')
        brandIds = self.request.GET.get('brandIds')

        withImages = ProductImage.objects.values_list('imageId', flat=True)
        items = items.filter(productId__in=withImages)

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

        # Фильтруем по значениям `productId`
        if productIds:
            items = items.filter(productId__in=productIds.split(','))
        return self.filter_queryset(items)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        availableSizes = ProductVariant.objects.filter(product__in=queryset).values_list('size', flat=True).distinct()

        serializer = self.get_serializer(page, many=True)
        return Response({
            'count': queryset.count(),
            'products': serializer.data,
            'filters': {
                'sizes': availableSizes
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
