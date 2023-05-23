from rest_framework.response import Response

from api.models import Product, ProductVariant
from .common import PRODUCT_VARIANT_FIELDS, PRODUCT_FIELDS, prepareFields, prepareVariantFields, getPodklads, getSostavs, firstSyncShouldBeHard
from api.utils import connectToPersonaDB
from django.core.cache import cache
from datetime import datetime
from pytz import utc, timezone
from celery import shared_task


@shared_task
def productSyncMid():
    try:
        lastMidSync = cache.get('products-last-sync-mid')
        if not lastMidSync:
            return Response({'error': firstSyncShouldBeHard}, status=400)
        lastMidSyncDate = utc.localize(
            datetime.strptime(lastMidSync, '%Y-%m-%d %H:%M:%S')
        )
        connection = connectToPersonaDB()
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT {PRODUCT_FIELDS} FROM mobper.Message2001 \
                WHERE Price = 0 AND Parent_Message_ID = 0;"
            )
            variableProducts = cursor.fetchall()
            # variableProducts = cursor.fetchmany(2)
            cursor.execute(
                f"SELECT {PRODUCT_FIELDS} FROM mobper.Message2001 \
                WHERE Price > 0 AND Parent_Message_ID = 0;"
            )
            singleProducts = cursor.fetchall()
            # singleProducts = cursor.fetchmany(2)
            cursor.execute(
                f"SELECT {PRODUCT_VARIANT_FIELDS} FROM mobper.Message2001 \
                WHERE Price > 0 AND Parent_Message_ID > 0;"
            )
            productVariants = cursor.fetchall()
            podklads = getPodklads()
            sostavs = getSostavs()

            for row in singleProducts:
                fields = prepareFields(
                    row, True,
                    podklads=podklads,
                    sostavs=sostavs
                )
                if fields['product']['lastUpdate'] <= lastMidSyncDate:
                    # filter(pk=uniqueId).exists() - самый быстрый способ проверки
                    if Product.objects.filter(pk=fields['uniqueId']).exists():
                        continue

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
            for row in variableProducts:
                fields = prepareFields(row, podklads=podklads, sostavs=sostavs)
                product, isCreated = Product.objects.update_or_create(
                    productId=fields['uniqueId'],
                    defaults=fields['product']
                )
                if fields['product']['lastUpdate'] <= lastMidSyncDate:
                    # filter(pk=uniqueId).exists() - самый быстрый способ проверки
                    if Product.objects.filter(pk=fields['uniqueId']).exists():
                        continue

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
            cache.set('products-last-sync-mid', dateNow)
            cache.set('products-last-sync-fast', dateNow)
            # return Response({'success': 'Синхронизация(2) продуктов прошла успешно'})
    except Exception as e:
        print(e)
        # return Response({'error': 'При синхронизации продуктов со сторонней БД произошла ошибка'}, status=400)
