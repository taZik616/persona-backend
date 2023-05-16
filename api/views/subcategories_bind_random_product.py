from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from api.models import Brand
from api.models import Category, CategoryLevel, Product


@api_view(['GET'])
# @permission_classes([IsAdminUser])
def subcategoriesBindRandomProduct(request):
    try:
        subCats = Category.objects.filter(level=CategoryLevel.SUBCATEGORY)
        for subCat in subCats:
            # order_by('?') - рандомная сортировка
            randomProduct = Product.objects.filter(
                subcategoryId=subCat.categoryId
            ).order_by('?').first()
            subCat.subcategoryPreviewProduct = randomProduct
            subCat.save()
        return Response({'success': 'Операция прошла успешно'})
    except:
        return Response({'error': 'Возникла ошибка, убедитесь что синхронизации были сделаны'}, status=400)
