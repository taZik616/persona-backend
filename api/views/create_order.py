import json
import re
import requests
from api.common_error_messages import SETTINGS_ERROR
from environment import SBER_API_PASSWORD, SBER_API_LOGIN, SBER_API_URL

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import UserInfoSerializer
from api.utils import splitString, selectAllFromProducts, getServerSettings
from api.models import ProductVariant, Order


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createOrder(request):
    try:
        productVariantIds = request.data.get('productVariantIds')

        if not productVariantIds:
            return Response({'error': 'Укажите товары которые хотите разместить в заказе'}, status=400)

        productVariantIds = splitString(productVariantIds)
        variants = ProductVariant.objects.filter(uniqueId__in=productVariantIds)
        if not variants.exists():
            return Response({'error': 'Ни один из указанных товаров не был найден'}, status=400)
        if variants.count() < len(productVariantIds):
            return Response({'error': 'Не удалось найти все товары которые вы указали'}, status=400)
        if variants.filter(isAvailable=False).exists():
            return Response({'error': 'Не все выбранные товары доступны для оформления'}, status=400)

        productsData = selectAllFromProducts(f'Message_ID in ({",".join(productVariantIds)})')

        createdOrder = Order.objects.create(
            productsInfo=productsData,
            costumerInfo=UserInfoSerializer(request.user).data,
            status='NotPaid',
            user=request.user
        )
        settings = getServerSettings()

        if not settings:
            return Response({'error': SETTINGS_ERROR}, status=400)

        # return Response({'success': 'Получилось', 'orderId': createdOrder.orderId})

        total = 0
        orderItems = []

        for item in productsData:
            itemsCount = 1
            price = int(item['price']) * 100
            preparedForOrderData = {
                'positionId': item['Message_ID'],
                'name': str(item['caption']).replace('"', '').replace("'", ""),
                'quantity': {'measure': 'штук', 'value': 1},
                'itemAmount': price * itemsCount,
                'itemPrice': price,
                'itemCurrency': '643',
                'itemCode': item['code'] if item['code'] else item['Message_ID']
            }

            discount = re.search(r"\d+%", item['priceGroup']) if item['priceGroup'] else ''
            if discount:
                discount = int(discount.group().strip("%"))
            else: 
                discount = 0

            if discount:
                preparedForOrderData['discount'] = {'discountType': 'percent', 'discountValue': discount}

            orderItems.append(preparedForOrderData)
            total += price * itemsCount

        deliveryCost = settings["delivery_cost_in_rub"]
        if deliveryCost:
            orderDelivery = {
                'positionId': 'delivery',
                'name': 'Доставка',
                'quantity': {'measure': 'штук', 'value': 1.00},
                'itemAmount': deliveryCost * 100,
                'itemPrice': deliveryCost * 100,
                'itemCurrency': '643',
                'itemCode': 'delivery'
            }

            orderItems.append(orderDelivery)
            total += deliveryCost * 100
        articles_list = [str(prod['code'] if prod['code'] else prod['Message_ID']) for prod in productsData]
        params = {
            'userName': settings["sber_api_login"],
            'password': settings["sber_api_password"],
            'currency': 643,
            'orderNumber': createdOrder.orderId,
            'description': f'Оплата заказа №{createdOrder.orderId} в магазине Персона. Артикулы покупаемых товаров: {", ".join(articles_list)}'[:512],
            'amount': total,
            'returnUrl': 'personashop://',
            'failUrl': 'personashop://',
            # 'orderBundle': {'cartItems': {'items': orderItems}}
        }

        registerUrl = f'{settings["sber_api_url"]}/register.do'
        data = requests.get(registerUrl, params=params, verify=False)
        return Response(data.json())
    except Exception as e:
        print(str(e))
        return Response({'error': 'При создании заказа возникла ошибка'}, status=400)