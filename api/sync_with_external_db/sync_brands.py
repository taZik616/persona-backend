from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api.models import Brand
from api.sync_with_external_db.utils.fetch_and_save_image import fetchAndSaveImage
from api.utils import connectToPersonaDB


@api_view(['POST'])
# @permission_classes([IsAdminUser])
def syncBrands(request):
    try:
        connection = connectToPersonaDB()
        with connection.cursor() as cursor:
            category_fields = 'Subdivision_ID, Subdivision_Name, Description, Keywords, logo, Checked'
            # К Parent_Sub_ID == 8 относятся бренды
            cursor.execute(
                f'SELECT {category_fields} FROM Subdivision WHERE Parent_Sub_ID = 8')
            brands = cursor.fetchall()
            for brand in brands:
                uniqueId, name, description, keywords, logoUrl, isTop = brand
                keywords = keywords if keywords is not None else ''
                description = description if description is not None else ''
                logoUrl = fetchAndSaveImage(logoUrl)
                Brand.objects.update_or_create(
                    brandId=uniqueId,
                    defaults={
                        'name': name,
                        'isTop': isTop,
                        'logoUrl': logoUrl,
                        'keywords': keywords,
                        'description': description,
                        'gender': 'men',  # Как узнать men/women?
                    }
                )
                cursor.execute(
                    f'SELECT {category_fields} FROM Subdivision WHERE Parent_Sub_ID = {uniqueId}'
                )
            return Response({'success': 'Синхронизация брендов прошла успешно'})
    except Exception as e:
        print(e)
        return Response({'error': 'При синхронизации брендов со сторонней БД произошла ошибка'}, status=400)
