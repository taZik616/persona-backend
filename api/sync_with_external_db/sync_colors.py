from PIL import Image
import requests
from io import BytesIO
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from api.models import Color
from api.utils import connectToPersonaDB
from celery import shared_task


@shared_task
def syncColorsTask():
    try:
        connection = connectToPersonaDB()
        with connection.cursor() as cursor:
            color_fields = 'Real_Name, File_Path, Virt_Name'
            cursor.execute(
                f'SELECT {color_fields} FROM Filetable WHERE File_Path = "/3/156/"'
            )
            colors = cursor.fetchall()

            for color in colors:
                name, siteDirectory, pathToImage = color
                name = removeExtension(name)

                url = f"https://personashop.com/netcat_files{siteDirectory}{pathToImage}"
                colorHex = colorHexFromImage(url)

                Color.objects.update_or_create(
                    name=name,
                    defaults={'hex': colorHex}
                )
            # return Response({'success': 'Синхронизация цветов прошла успешно'})
    except Exception as e:
        print(e)
        # return Response({'error': 'При синхронизации цветов со сторонней БД произошла ошибка'}, status=400)
    
@api_view(['POST'])
@permission_classes([IsAdminUser])
def syncColors(request):
    syncColorsTask.delay()
    return Response({'success': 'Синхронизация цветов была запущенна'})


def colorHexFromImage(imageUrl):
    response = requests.get(imageUrl)
    response.raise_for_status()

    imageData = BytesIO(response.content)
    image = Image.open(imageData)
    histogram = image.histogram()

    maxCountIndex = max(range(len(histogram)), key=histogram.__getitem__)
    maxCountIndex = min(maxCountIndex, image.width - 1)

    rgbColor = image.getpixel((maxCountIndex, 0))
    # Преобразуем RGB-значение цвета в формат хэш-значения
    hexColor = '#{:02x}{:02x}{:02x}'.format(*rgbColor)
    return hexColor


def removeExtension(filename):
    lastDotIndex = filename.rfind('.')
    if lastDotIndex != -1:
        return filename[:lastDotIndex]
    else:
        return filename
