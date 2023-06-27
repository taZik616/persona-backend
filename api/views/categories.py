from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from api.models import Category, CategoryLevel
from api.serializers import CategorySerializer


class CategoryListView(ListAPIView):
    serializer_class = CategorySerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['level', 'gender']
    filterset_fields = ['parentId', 'gender', 'level']
    ordering = ['level', 'gender']

    def get_queryset(self):
        items = Category.objects.all()
        level = self.request.GET.get('level')
        parentId = self.request.GET.get('parentId')

        if (level and int(level) == CategoryLevel.SUBCATEGORY) or parentId:
            items = items.filter(subcategoryPreviewProduct__isnull=False)
        return self.filter_queryset(items)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
