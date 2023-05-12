from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api.models import Product, ProductCharacteristic, ProductVariant, Brand, Category
from .utils import groupBy, getDescriptionForProductFields
from api.utils import connectToPersonaDB
import re
from django.core.cache import cache
from datetime import datetime
from pytz import utc
from django.utils.timezone import make_aware


@api_view(['POST'])
# @permission_classes([IsAdminUser])
def syncProducts(request):
    try:
        connection = connectToPersonaDB()
        # descriptionName, podkladName, countryName, \
        #     sostavName, manufacturerName = getDescriptionForProductFields().values()

        with connection.cursor() as cursor:
            # Parent_Message_ID - великий ID по которому можно определить однотипность товаров
            product_fields = 'caption, price, Subdivision_ID, Message_ID, Parent_Message_ID, brand, size, color, stock, new, ncKeywords, priceGroup, manufacturer, country, podklad, sostav, collection, LastUpdated'

            cursor.execute(
                f"SELECT {product_fields} FROM `mobper`.`Message2001` WHERE Price > 0 AND Parent_Message_ID > 0;"
            )
            elements = cursor.fetchmany(20)
            # elements = cursor.fetchall()
            groups = groupBy(list(elements), 4)
            for group in groups:
                firstPrice = group[0][1]
                withSamePrice = filter(lambda x: x[1] == firstPrice, group)
                product: Product = None

                for index, row in enumerate(withSamePrice):
                    productName, price, subcategoryId, uniqueId, productId, \
                        brandName, size, color, isAvailable, isNew, \
                        keywords, priceGroup, manufacturer, country, \
                        podklad, sostav, collection, lastUpdate = row

                    lastUpdate = utc.localize(lastUpdate)

                    lastSync = cache.get('products-last-sync')
                    if lastSync:
                        lastSyncDate = datetime.strptime(
                            lastSync, '%Y-%m-%d %H:%M:%S')
                        if lastUpdate <= utc.localize(lastSyncDate):
                            # filter(pk=productId).exists() - самый быстрый способ проверки
                            if Product.objects.filter(pk=productId).exists():
                                continue

                    keywords = keywords if keywords is not None else ''
                    collection = collection if collection is not None else ''
                    priceGroup = priceGroup if priceGroup is not None else ''
                    manufacturer = manufacturer if manufacturer is not None else ''
                    country = country if country is not None else ''
                    podklad = podklad if podklad is not None else ''
                    sostav = sostav if sostav is not None else ''
                    # Я не хочу снова писать ниже все что выше, поэтому делаю так
                    if index == 0:
                        brand = None
                        try:
                            brand = Brand.objects.get(name=brandName)
                        except Brand.DoesNotExist:
                            brand = None

                        categoryId = Category.objects.get(
                            categoryId=subcategoryId).parentId
                        updated_product, isCreated = Product.objects.update_or_create(
                            productId=productId,
                            defaults={
                                'price': price,
                                'brand': brand,
                                'collection': collection,
                                'keywords': keywords,
                                'subcategoryId': subcategoryId,
                                'categoryId': categoryId,
                                # Тут удаляем информацию в скобках `()`
                                'productName': re.sub(
                                    r'\s*\([^)]*\)$', '', str(productName)),
                                'isAvailable': bool(isAvailable),
                                'isNew': bool(isNew),
                                'priceGroup': priceGroup,
                                'lastUpdate': lastUpdate
                            }
                        )
                        product = updated_product
                        ProductCharacteristic.objects.update_or_create(
                            id=productId,
                            defaults={
                                'product': product,
                                'manufacturer': manufacturer,
                                'country': country,
                                'podklad': podklad,
                                'sostav': sostav
                            }

                        )

                    ProductVariant.objects.update_or_create(
                        uniqueId=uniqueId,
                        defaults={
                            'size': size,
                            'color': color,
                            'product': product
                        }
                    )
            dateNow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cache.set('products-last-sync', dateNow)
            return Response({'success': 'Синхронизация продуктов прошла успешно'})
    except Exception as e:
        print(e)
        return Response({'error': 'При синхронизации продуктов со сторонней БД произошла ошибка'}, status=400)
