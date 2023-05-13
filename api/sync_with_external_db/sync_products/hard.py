from rest_framework.response import Response

from api.models import Product, ProductVariant
from .common import PRODUCT_VARIANT_FIELDS, PRODUCT_FIELDS, prepareFields, prepareVariantFields, getPodklads, getSostavs
from api.utils import connectToPersonaDB
from django.core.cache import cache
from datetime import datetime
from pytz import timezone


def productSyncHard():
    try:
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

            Product.objects.all().delete()
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

                for variant in variants:
                    varFields = prepareVariantFields(variant)
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
            return Response({'success': 'Синхронизация(3) продуктов прошла успешно'})
    except Exception as e:
        print(e)
        return Response({'error': 'При синхронизации продуктов со сторонней БД произошла ошибка'}, status=400)
