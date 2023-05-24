from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api.models import Category, CategoryLevel
from api.utils import connectToPersonaDB
from celery import shared_task


@shared_task
def syncCategoriesTask():
    try:
        connection = connectToPersonaDB()
        with connection.cursor() as cursor:

            category_fields = 'Subdivision_ID, Parent_Sub_ID, Subdivision_Name, Description, Keywords'
            # 178 - это товары для мужчин
            cursor.execute(
                f'SELECT {category_fields} FROM Subdivision WHERE Parent_Sub_ID = 178')
            menCategories = cursor.fetchall()
            # 177 - это товары для женщин
            cursor.execute(
                f'SELECT {category_fields} FROM Subdivision WHERE Parent_Sub_ID = 177')
            womenCategories = cursor.fetchall()

            for index, rows in enumerate([menCategories, womenCategories]):
                gender = 'men' if index == 0 else 'women'
                for row in rows:
                    uniqueId, parentId, name, description, keywords = row
                    keywords = keywords if keywords is not None else ''
                    description = description if description is not None else ''
                    Category.objects.update_or_create(
                        categoryId=uniqueId,
                        defaults={
                            'parentId': parentId,
                            'name': name,
                            'description': description,
                            'keywords': keywords,
                            'level': CategoryLevel.CATEGORY,
                            'gender': gender
                        }
                    )
                    cursor.execute(
                        f'SELECT {category_fields} FROM Subdivision WHERE Parent_Sub_ID = {uniqueId}'
                    )
                    subcategories = cursor.fetchall()
                    for subcategory in subcategories:
                        subCatUniqueId, subCatParentId, subCatName, \
                            subCatDescription, subCatKeywords = subcategory
                        subCatKeywords = subCatKeywords if subCatKeywords is not None else ''
                        subCatDescription = subCatDescription if subCatDescription is not None else ''
                        Category.objects.update_or_create(
                            categoryId=subCatUniqueId,
                            defaults={
                                'parentId': subCatParentId,
                                'name': subCatName,
                                'description': subCatDescription,
                                'keywords': subCatKeywords,
                                'level': CategoryLevel.SUBCATEGORY,
                                'gender': gender
                            }
                        )
            # return Response({'success': 'Синхронизация категорий и подкатегорий прошла успешно'})
    except Exception as e:
        print(e)
        # return Response({'error': 'При синхронизации категорий и подкатегорий со сторонней БД произошла ошибка'}, status=400)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def syncCategories(request):
    syncCategoriesTask.delay()
    return Response({'success': 'Синхронизация категорий была запущенна'})
