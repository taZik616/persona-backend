from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .hard import productSyncHard
from .mid import productSyncMid
from .fast import productSyncFast

# Варианты синхронизации:
# 1. Только по дате обновления:
#     - Запрашиваются товары, у которых время LastUpdated относительно прошлой такой
#     синхронизации больше, и соответствующие им продукты создаются/обновляются.
#     - Это самый быстрый вариант синхронизации(если вызов происходит не первый раз)
#     - Тут будет использоваться кеш под ключом `products-last-sync-fast`
# 2. Запрашиваем все и при необходимости обновляем/создаем товар:
#     - Этот вариант синхронизации отлично подходит если мы удалили из таблицы товары
#     и их нужно восстановить
#     - Запрашиваются все товары. Затем мы сверяем кеш даты последней успешной синхронизации
#     и LastUpdated из запроса(благодаря кешу `products-last-sync-mid`, не нужно искать
#     товар для того чтобы с него вытащить lastUpdate для сравнения).
#     Если товара нету, то он создается
#     - Тут будет использоваться кеш под ключом `products-last-sync-mid`
# 3. Жесткая синхронизация:
#    - Тут все продукты удаляются и создаются с нуля
#    - Идеально если вызвать в первый раз, никаких проверок по дате последнего обновления
#    происходить не будет

AvailableSyncVariants = [1, 2, 3]


@api_view(['POST'])
# @permission_classes([IsAdminUser])
def syncProducts(request):
    syncVariant = int(request.data.get('syncVariant', 3))

    if syncVariant not in AvailableSyncVariants:
        return Response({'error': 'Недопустимое значение варианта синхронизации'}, status=400)

    if syncVariant == 3:
        return productSyncHard()
    if syncVariant == 2:
        return productSyncMid()
    if syncVariant == 1:
        return productSyncFast()

# descriptionName, podkladName, countryName, \
#     sostavName, manufacturerName = getDescriptionForProductFields().values()
