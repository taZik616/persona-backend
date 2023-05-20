import mimetypes
from uuid import uuid4
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.core.files.base import ContentFile
from api.models import Brand
from api.utils import connectToPersonaDB


@api_view(['POST'])
@permission_classes([IsAdminUser])
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

                filePath = logoUrl[logoUrl.rindex(':') + 1:]
                url = f"https://personashop.com/netcat_files/{filePath}"
                response = requests.get(url)
                fileExtension = mimetypes.guess_extension(
                    response.headers.get("content-type"))
                if not fileExtension:
                    continue

                fileName = f"{uuid4()}{fileExtension}"

                brand, isCreated = Brand.objects.update_or_create(
                    brandId=uniqueId,
                    defaults={
                        'name': name,
                        'isTop': isTop,
                        'keywords': keywords,
                        'description': description,
                        'gender': 'men',  # Как узнать men/women?
                    }
                )
                brand.logo.save(fileName, ContentFile(response.content))
            return Response({'success': 'Синхронизация брендов прошла успешно'})
    except Exception as e:
        print(e)
        return Response({'error': 'При синхронизации брендов со сторонней БД произошла ошибка'}, status=400)
