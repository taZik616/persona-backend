from api.models import ProductImage
from api.utils import connectToPersonaDB, splitString
import requests
from .utils import compressImage
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
import mimetypes
from uuid import uuid4
from django.core.files.base import ContentFile


# Варианты синхронизации:
# 1. Загрузка картинкок, которых еще нету:
#     - Добавляем картинки с Message_ID, которых нет в записях Базы данных
#     - Подходит если были добавлены новые картинки с Message_ID которого раньше не было
# 2. Обновить картинки с какими-то определенными Message_ID:
#     - Удаляем все старые картинки под определенным Message_ID и заново загружаем уже новые
#     - Подходит если картинки каких-либо продуктов были обновлены и вам известно под какими они Message_ID
# 3. Жесткая:
#    - Удаляем все картинки, которые были загружены до этого и загружаем все заново с обновлениями
#    - Подходит если вы псих или же если ни разу еще этого не делалось

AvailableSyncVariants = [1, 2, 3]

# Так этот комент для меня, сейчас проблема с файлами без разрешения в кнце пути:
# "/netcat_files/multifile/2281/0e322374926e43ff4b22476d2a195a05"
# Сейчас стоит проверка что "2281" не включается в путь до файла. Если что-то пойдет
# не так, то нужно проверять в ссылке наличие формата файла(ну или при парсинге формата это обрабатывать)


@api_view(['POST'])
# @permission_classes([IsAdminUser])
def syncImages(request):
    syncVariant = int(request.data.get('syncVariant', 2))
    idsToUpdate = request.data.get('idsToUpdate')

    if syncVariant not in AvailableSyncVariants:
        return Response({'error': 'Недопустимое значение варианта синхронизации'}, status=400)

    if syncVariant == 1:
        return syncImagesWhichNotHere()
    if syncVariant == 2:
        if not idsToUpdate:
            return Response({'error': 'Для обновления картинок по IDs нужно указать их через запятую в поле "idsToUpdate"'}, status=400)
        ids = splitString(idsToUpdate)
        return syncImagesByIds(ids)
    if syncVariant == 3:
        return syncImagesHard()


BASE_URL = 'https://personashop.com'


def syncImagesWhichNotHere():
    try:
        connection = connectToPersonaDB()
        with connection.cursor() as cursor:
            # Получаем список идентификаторов(без повторений) картинок продуктов
            existIds = ProductImage.objects.values_list(
                'imageId', flat=True).distinct()

            cursor.execute(
                f"SELECT Message_ID, Priority, Path FROM Multifield WHERE Message_ID NOT IN ({','.join(existIds)})"
            )
            images = cursor.fetchall()
            images = sorted(images, key=lambda image: image[0])
            for row in images:
                imageId, priority, imagePath = row
                if '2281' in imagePath:
                    continue

                response = requests.get(BASE_URL + imagePath)
                fileExtension = mimetypes.guess_extension(
                    response.headers.get("content-type"))
                if not fileExtension:
                    continue

                compressedImage = compressImage(
                    response.content, fileExtension[1:])

                fileName = f"{uuid4()}{fileExtension}"
                imageInstance = ProductImage()

                imageInstance.imageId = imageId
                imageInstance.priority = int(priority)
                imageInstance.originalImage.save(
                    fileName, ContentFile(response.content))
                imageInstance.compressedImage.save(
                    fileName, ContentFile(compressedImage))
                imageInstance.save()
            return Response({'success': 'Синхронизация(1) картинок прошла успешно'})
    except Exception as e:
        print(e)
        return Response({'error': 'При синхронизации картинок со сторонней БД произошла ошибка'}, status=400)


def syncImagesByIds(ids: list):
    try:
        connection = connectToPersonaDB()
        with connection.cursor() as cursor:
            messageIds = ','.join(ids)

            cursor.execute(
                f"SELECT Message_ID, Priority, Path FROM Multifield WHERE Message_ID IN ({messageIds})"
            )
            images = cursor.fetchall()
            images = sorted(images, key=lambda image: image[0])
            for id in ids:
                ProductImage.objects.filter(imageId=id).delete()
            for row in images:
                imageId, priority, imagePath = row
                if '2281' in imagePath:
                    continue

                response = requests.get(BASE_URL + imagePath)
                fileExtension = mimetypes.guess_extension(
                    response.headers.get("content-type"))

                if not fileExtension:
                    continue

                compressedImage = compressImage(
                    response.content, fileExtension[1:])

                fileName = f"{uuid4()}{fileExtension}"
                imageInstance = ProductImage()

                imageInstance.imageId = imageId
                imageInstance.priority = int(priority)
                imageInstance.originalImage.save(
                    fileName, ContentFile(response.content))
                imageInstance.compressedImage.save(
                    fileName, ContentFile(compressedImage))
                imageInstance.save()
            return Response({'success': 'Синхронизация(2) картинок прошла успешно'})
    except Exception as e:
        print(e)
        return Response({'error': 'При синхронизации картинок со сторонней БД произошла ошибка'}, status=400)


def syncImagesHard():
    try:
        connection = connectToPersonaDB()
        ProductImage.objects.all().delete()
        with connection.cursor() as cursor:
            cursor.execute("SELECT Message_ID, Priority, Path FROM Multifield")
            images = cursor.fetchall()
            images = sorted(images, key=lambda image: image[0])
            for row in images:
                imageId, priority, imagePath = row
                if '2281' in imagePath:
                    continue

                response = requests.get(BASE_URL + imagePath)
                fileExtension = mimetypes.guess_extension(
                    response.headers.get("content-type"))
                if not fileExtension:
                    continue

                compressedImage = compressImage(
                    response.content, fileExtension[1:])

                fileName = f"{uuid4()}{fileExtension}"
                imageInstance = ProductImage()

                imageInstance.imageId = imageId
                imageInstance.priority = int(priority)
                imageInstance.originalImage.save(
                    fileName, ContentFile(response.content))
                imageInstance.compressedImage.save(
                    fileName, ContentFile(compressedImage))
                imageInstance.save()
            return Response({'success': 'Синхронизация картинок прошла успешно'})
    except:
        return Response({'error': 'При синхронизации картинок со сторонней БД произошла ошибка'}, status=400)
