from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api.models import Brand, Product, ProductImage
from api.utils import getWomenAndMenCats


@api_view(['POST'])
@permission_classes([IsAdminUser])
def brandsGenderSeparate(request):
    try:
        items = Product.objects.select_related(
            'brand').filter(isAvailable=True, checked=True)

        withImages = ProductImage.objects.values_list('imageId', flat=True)
        items = items.filter(productId__in=withImages)
        [menCats, womenCats] = getWomenAndMenCats()

        menProds = items.filter(categoryId__in=menCats)
        womenProds = items.filter(categoryId__in=womenCats)

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
            else:
                brand.gender = None
            brand.save()
        return Response({'success': 'Разделение брендов на муж/жен/оба прошло успешно'})
    except Exception as e:
        print(str(e))
        return Response({'error': 'При разделении брендов возникла ошибка'}, status=400)
