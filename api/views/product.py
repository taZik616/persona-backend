from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from api.models import Product, ProductImage, ProductVariant
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
        'isNew', 'subcategoryId', 'categoryId', 'brand__brandId'  # 'productId',
    ]
    ordering = ['-lastUpdate']
    search_fields = [
        'productName', 'collection', 'description',
        'keywords', 'brand__name', 'brand__keywords'
    ]

    def get_queryset(self):
        items = Product.objects.select_related(
            'brand').filter(isAvailable=True)
        productIds = self.request.GET.get('productId', '').split(',')

        # Фильтруем по значениям `productId`
        if productIds:
            items = items.filter(productId__in=productIds)
        return self.filter_queryset(items)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        images_dict = {}

        imageIds = [product.productId for product in page]

        # Получаем соответствующие картинки для каждого идентификатора
        images = ProductImage.objects.filter(imageId__in=imageIds)
        for image in images:
            if image.imageId not in images_dict:
                images_dict[image.imageId] = []

            images_dict[image.imageId].append(image)

        # Сохраняем картинки в каждом товаре
        for product in page:
            product.images = sorted(
                images_dict.get(product.productId, []),
                key=lambda image: image.priority
            )
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)


class ProductDetailView(RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()
    lookup_field = 'productId'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        variants = ProductVariant.objects.filter(product=instance)

        # Получаем соотvariants = ProductVariant.objects.filter(product=instance)ветствующие картинки для каждого идентификатора
        images = ProductImage.objects.filter(imageId=instance.productId)

        # Добавляем картинки в сериализатор товара
        instance.images = sorted(
            images, key=lambda image: image.priority
        )
        instance.variants = variants

        return Response(self.get_serializer(instance).data)
