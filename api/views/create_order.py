import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.common_error_messages import SETTINGS_ERROR
from api.models import GiftCard, Order, ProductVariant, Promocode
from api.serializers import UserInfoSerializer
from api.utils import getServerSettings, selectAllFromProducts, splitString
from api.views.check_order_status import checkOrderStatusAndUpdateStateTask
from api.views.order_personal_discount_calc import orderPersonalDiscountCalc


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createOrder(request):
    productVariantIds = request.data.get('productVariantIds', '')
    address = request.data.get('address', '')
    promocode = request.data.get('promocode', '')

    if not address:
        return Response({'error': 'Укажите адрес на который нужно отправить заказ'}, status=400)
    if not productVariantIds:
        return Response({'error': 'Укажите товары которые хотите разместить в заказе'}, status=400)
    giftCard = GiftCard.objects.filter(promocode=promocode).first()
    if giftCard and giftCard.isBlocked:
        return Response({'error': 'Подарочноя карта временно заморожена, после проверки сделанного заказа вы сможете продолжить ей пользоваться'}, status=400)
    if giftCard and not giftCard.isActive:
        return Response({'error': 'Карта не активирована, для активации нужно оплатить заказ'}, status=400)
    orderData = orderPersonalDiscountCalc(
        productVariantIds, request.user, promocode, request)

    if orderData.get('error'):
        return Response(orderData, status=400)
    orderPrice = orderData['priceWithPersonalDiscount'] * 100

    createdOrder: Order
    try:
        productVariantIds = splitString(productVariantIds)
        variants = ProductVariant.objects.filter(
            uniqueId__in=productVariantIds)
        if not variants.exists():
            return Response({'error': 'Ни один из указанных товаров не был найден'}, status=400)
        if variants.count() < len(productVariantIds):
            return Response({'error': 'Не удалось найти все товары которые вы указали'}, status=400)
        if variants.filter(isAvailable=False).exists():
            return Response({'error': 'Не все выбранные товары доступны для оформления'}, status=400)

        productsData = selectAllFromProducts(
            f'Message_ID in ({",".join(productVariantIds)})')

        settings = getServerSettings()
        if not settings:
            return Response({'error': SETTINGS_ERROR}, status=400)

        createdOrder = Order.objects.create(
            productsLegacyInfo=productsData,
            productsInfo=orderData['products'],
            costumerInfo=UserInfoSerializer(request.user).data,
            status='NotPaid',
            user=request.user,
            address=address
        )

        deliveryCost = settings["delivery_cost_in_rub"]
        if deliveryCost:
            orderPrice += deliveryCost * 100

        articles = [str(prod['code'] if prod['code'] else prod['Message_ID'])
                    for prod in productsData]
        params = {
            'userName': settings["sber_api_login"],
            'password': settings["sber_api_password"],
            'currency': 643,
            'orderNumber': createdOrder.orderId,
            'description': f'Оплата заказа №{createdOrder.orderId} в магазине Персона. Артикулы покупаемых товаров: {", ".join(articles)}'[:512],
            'amount': int(orderPrice),
            'returnUrl': 'personashop://order-pay-success',
            'failUrl': 'personashop://order-pay-failed'
        }

        registerUrl = f'{settings["sber_api_url"]}/register.do'
        data = requests.get(registerUrl, params=params, verify=False).json()
        if data.get('orderId'):
            createdOrder.orderSberId = data['orderId']
            createdOrder.usedPromocode = Promocode.objects.filter(
                code=promocode).first()
            createdOrder.save()

            if giftCard:
                giftCard.isBlocked = True
                giftCard.save()
            checkOrderStatusAndUpdateStateTask.apply_async(
                args=[data['orderId']],
                kwargs={'giftCardUsed': True, 'giftCardPromocode': promocode},
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
