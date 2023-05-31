from ..models import Brand, Category, Product
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([IsAdminUser])
def brandsGenderSeparate(request):
    try:
        menCats = Category.objects.filter(level=1, gender='men').values_list('categoryId', flat=True)
        womenCats = Category.objects.filter(level=1, gender='women').values_list('categoryId', flat=True)
        menCats = [str(catId) for catId in menCats]
        womenCats = [str(catId) for catId in womenCats]

        menProds = Product.objects.filter(categoryId__in=menCats)
        womenProds = Product.objects.filter(categoryId__in=womenCats)

        brands = Brand.objects.all()
        for brand in brands:
            male_count = menProds.filter(brand=brand).count()
            female_count = womenProds.filter(brand=brand).count()

            if male_count > 0 and female_count > 0:
                brand.gender = 'both'
            elif male_count > 0:
                brand.gender = 'men'
            elif female_count > 0:
                brand.gender = 'women'
            brand.save()
        return Response({'success': 'Разделение брендов на муж/жен/оба прошло успешно'})
    except Exception as e:
        print(str(e))
        return Response({'error': 'При разделении брендов возникла ошибка'}, status=400)