import re
import requests
from api.common_error_messages import SETTINGS_ERROR

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import UserInfoSerializer
from api.utils import splitString, selectAllFromProducts, getServerSettings
from api.models import ProductVariant, Order
from api.views.check_order_status import checkOrderStatusAndUpdateStateTask


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createOrder(request):
    createdOrder: Order
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

        settings = getServerSettings()

        if not settings:
            return Response({'error': SETTINGS_ERROR}, status=400)
        
        createdOrder = Order.objects.create(
            productsInfo=productsData,
            costumerInfo=UserInfoSerializer(request.user).data,
            status='NotPaid',
            user=request.user
        )

        orderPrice = 0

        for item in productsData:
            itemsCount = 1
            price = int(item['price']) * 100

            discount = re.search(r"\d+%", item['priceGroup']) if item['priceGroup'] else ''
            if discount:
                discount = int(discount.group().strip("%"))
                if discount <= 100:
                    price = price - (price / 100 * discount)
            else: 
                discount = 0

            orderPrice += price * itemsCount

        deliveryCost = settings["delivery_cost_in_rub"]
        if deliveryCost:
            orderPrice += deliveryCost * 100
        articles_list = [str(prod['code'] if prod['code'] else prod['Message_ID']) for prod in productsData]
        params = {
            'userName': settings["sber_api_login"],
            'password': settings["sber_api_password"],
            'currency': 643,
            'orderNumber': createdOrder.orderId,
            'description': f'Оплата заказа №{createdOrder.orderId} в магазине Персона. Артикулы покупаемых товаров: {", ".join(articles_list)}'[:512],
            'amount': int(orderPrice),
            'returnUrl': 'personashop://',
            'failUrl': 'personashop://'
        }

        registerUrl = f'{settings["sber_api_url"]}/register.do'
        data = requests.get(registerUrl, params=params, verify=False).json()
        if data.get('orderId'):
            createdOrder.orderSberId = data['orderId']
            createdOrder.save()
            checkOrderStatusAndUpdateStateTask.apply_async(
                args=[data['orderId']],
                countdown=settings["sber_api_payment_time_limit"]
            )
        return Response({
            **data,
            'orderIdInBackend': createdOrder.orderId
        })
    except Exception as e:
        print(str(e))
        if createdOrder:
            createdOrder.delete()
        return Response({'error': 'При создании заказа возникла ошибка'}, status=400)
    
# return Response({'success': 'Получилось', 'orderId': createdOrder.orderId})