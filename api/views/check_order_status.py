from functools import reduce

import requests
from celery import shared_task
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.common_error_messages import SETTINGS_ERROR
from api.models import FastOrder, GiftCard, Order
from api.models.discount_card import DiscountCard
from api.serializers.order import OrderSerializer
from api.utils import getServerSettings


@shared_task
def checkOrderStatusAndUpdateStateTask(orderId, isFastOrder=False, giftCardUsed=False, giftCardPromocode=''):
    '''
    `orderId` - идентификатор который выдает сбербанк
    '''
    try:
        if not orderId:
            return {'error': 'Вы не указали идентификатор заказа'}

        settings = getServerSettings()
        if not settings:
            return {'error': SETTINGS_ERROR}

        url = f'{settings["sber_api_url"]}/getOrderStatusExtended.do'
        params = {
            'userName': settings['sber_api_login'],
            'password': settings['sber_api_password'],
            'orderId': orderId
        }

        response = requests.get(url, params=params, verify=False)
        data = response.json()
        if data.get('orderStatus') != None and data.get('orderNumber') != None:
            order = None
            if isFastOrder:
                order = FastOrder.objects.filter(
                    orderId=data['orderNumber']).first()
            else:
                order = Order.objects.filter(
                    orderId=data['orderNumber']).first()
            if not order:
                return {'error': 'Не удалось найти заказ'}
            # После прошествия 20 мин разблокируем карту
            giftCard = GiftCard.objects.filter(
                promocode=giftCardPromocode).first()
            if (giftCard and giftCardUsed and giftCard.isBlocked) or (giftCard and data['orderStatus'] == 2 and giftCard.isBlocked):
                giftCard.isBlocked = False
                totalPersonalDiscount = reduce(
                    lambda prev, a: prev + int(a.get('personalDiscountInRub', 0)), order.productsInfo, 0)
                giftCard.balance = int(giftCard.balance) - \
                    int(totalPersonalDiscount)
                giftCard.save()
            if order.status not in ['Delivery', 'Received', 'AlreadyPaid']:
                match data['orderStatus']:
                    case 2:
                        if not isFastOrder:
                            if order.usedPromocode:
                                order.user.usedPromocodes.add(
                                    order.usedPromocode)
                                discountCard = DiscountCard.objects.filter(
                                    user=order.user).first()
                                if discountCard:
                                    # Ну мне лень еще раз реализовывать подсчет цены
                                    discountCard.purchaseTotal += OrderSerializer(
                                        order).data['totalSum']
                                    discountCard.save()
                                order.user.save()
                        order.status = 'AlreadyPaid'
                    case 3:
                        order.status = 'Mistaken'
                    case 4:
                        order.status = 'Mistaken'
                order.save()

        return data
    except Exception as e:
        print(e)
        return {'error': 'Не удалось узнать статус заказа'}


@api_view(['POST'])
def checkOrderStatus(request):
    orderId = request.data.get('orderId')
    data = checkOrderStatusAndUpdateStateTask(orderId)

    if data.get('error'):
        dataFast = checkOrderStatusAndUpdateStateTask(orderId, True)
        if dataFast.get('error'):
            return Response(dataFast, status=400)
        else:
            return Response(dataFast)
    else:
        return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateAllOwnOrdersStatus(request):
    try:
        orders = Order.objects.filter(user=request.user)
        giftBlockedCards = GiftCard.objects.filter(
            isBlocked=True, user=request.user)
        for order in orders:
            # Я бы мог в ордер записывать промокод подарочной карты но я это поздно понял(когда наполнил БД )
            for blockedCard in giftBlockedCards:
                checkOrderStatusAndUpdateStateTask(
                    order.orderSberId, giftCardPromocode=blockedCard.promocode)
            #
            data = checkOrderStatusAndUpdateStateTask(order.orderSberId)
            if data.get('error'):
                checkOrderStatusAndUpdateStateTask(order.orderSberId, True)
        return Response({'success': 'Операция прошла успешно'})
    except Exception as e:
        print(e)
        return Response({'error': 'Неизвестная ошибка'}, status=400)
