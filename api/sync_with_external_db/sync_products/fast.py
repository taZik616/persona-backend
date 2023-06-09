import re
from datetime import datetime

from celery import shared_task
from django.core.cache import cache
from pytz import timezone
from rest_framework.response import Response

from api.models import Product, ProductVariant
from api.utils import connectToPersonaDB

from .common import (PRODUCT_FIELDS, PRODUCT_VARIANT_FIELDS,
                     firstSyncShouldBeHard, getPodklads, getSostavs,
                     prepareFields, prepareVariantFields)


@shared_task
def productSyncFast():
    try:
        connection = connectToPersonaDB()
        with connection.cursor() as cursor:
            lastFastSync = cache.get('products-last-sync-fast')
            if not lastFastSync:
                return Response({'error': firstSyncShouldBeHard}, status=400)

            podklads = getPodklads()
            sostavs = getSostavs()

            cursor.execute(
                f"SELECT {PRODUCT_FIELDS} FROM mobper.Message2001 \
                WHERE Price > 0 AND Parent_Message_ID = 0 AND LastUpdated >= '{lastFastSync}' AND Subdivision_ID != 224;"
            )
            # Одиночные продукты, которые имеют только одну конфигурацию
            singleProducts = cursor.fetchall()

            for row in singleProducts:
                fields = prepareFields(
                    row, True,
                    podklads=podklads,
                    sostavs=sostavs
                )

                product, isCreated = Product.objects.update_or_create(
                    productId=fields['uniqueId'],
                    defaults=fields['product']
                )
                ProductVariant.objects.update_or_create(
                    uniqueId=fields['uniqueId'],
                    defaults={
                        **fields['variantForSingleProduct'],
                        'product': product
                    }
                )

            cursor.execute(
                f"SELECT {PRODUCT_FIELDS} FROM mobper.Message2001 \
                WHERE Price = 0 AND Parent_Message_ID = 0 AND LastUpdated >= '{lastFastSync}' AND Subdivision_ID != 224;"
            )
            # Вариативные продукты, у которых есть детишки привязанные по `Parent_Message_ID`
            variableProducts = cursor.fetchall()
            variableProductsIds = ','.join(
                str(item[2]) for item in variableProducts)

            if not variableProductsIds:
                return Response({'success': 'Синхронизация(1) продуктов прошла успешно'})
            cursor.execute(
                f"SELECT {PRODUCT_VARIANT_FIELDS} FROM mobper.Message2001 \
                WHERE Price > 0 AND Parent_Message_ID IN ({variableProductsIds}); AND Subdivision_ID != 224"
            )
            # Варианты вариативных продуктов
            productVariants = cursor.fetchall()

            for row in variableProducts:
                fields = prepareFields(row, podklads=podklads, sostavs=sostavs)
                product, isCreated = Product.objects.update_or_create(
                    productId=fields['uniqueId'],
                    defaults=fields['product']
                )

                variants = list(
                    filter(lambda x: x[2] == fields['uniqueId'], productVariants))
                productVariants = list(
                    filter(lambda x: x[2] != fields['uniqueId'], productVariants))

                isOneAvailable = any(
                    variant[5] for variant in variants
                )
                product.isAvailable = isOneAvailable
                product.save()
                for variant in variants:
                    varFields = prepareVariantFields(variant)

                    if not product.price and varFields['isAvailable']:
                        product.price = varFields['price']
                        product.priceGroup = varFields['priceGroup']
                        discount = re.search(
                            r"\d+%", varFields['priceGroup']) if varFields['priceGroup'] else ''
                        if discount:
                            discount = int(discount.group().strip("%"))
                        else:
                            discount = 0
                        product.discountPercent = discount
                        product.isAvailable = True
                        product.save()
                    ProductVariant.objects.update_or_create(
                        uniqueId=varFields['uniqueId'],
                        defaults={
                            **varFields,
                            'product': product
                        }
                    )
            tz = timezone('Europe/Moscow')
            dateNow = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            cache.set('products-last-sync-fast', dateNow)
            # return Response({'success': 'Синхронизация(1) продуктов прошла успешно'})
    except Exception as e:
        print(e)
        # return Response({'error': 'При синхронизации продуктов со сторонней БД произошла ошибка'}, status=400)
