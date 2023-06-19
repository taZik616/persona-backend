from api.common_error_messages import SETTINGS_ERROR
from api.utils import getServerSettings
from rest_framework.response import Response
import requests
from celery import shared_task

from api.models import GiftCard, GiftCardType
from api.serializers import GiftCardSerializer, GiftCardTypeSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@shared_task
def checkGiftCardOrderStatusAndUpdateStateTask(orderId: str):
    if not orderId:
        return {'error': 'Вы не указали идентификатор заказа'}
    try:
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
            giftCard = GiftCard.objects.filter(pk=data['orderNumber']).first()
            if not giftCard:
                return {'error': 'Не удалось найти подарочную карту'}
            if data['orderStatus'] == 2:
                giftCard.isActive = True
                giftCard.save()

        return data
    except Exception as e:
        print(e)
        return {'error': 'Не удалось узнать статус заказа'}

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOwnMintedGiftCards(request):
    try:
        giftCards = GiftCard.objects.filter(user=request.user)
        return Response(GiftCardSerializer(giftCards, many=True, context={'request': request}).data)
    except Exception as e:
        print(e)
        return Response({'error': 'Не удалось вернуть список созданных вами подарочных карт'}, status=400)
    
@api_view(['GET'])
def getGiftCardTypes(request):
    try:
        giftCardTypes = GiftCardType.objects.all()
        return Response(GiftCardTypeSerializer(giftCardTypes, many=True, context={'request': request}).data)
    except:
        return Response({'error': 'Не удалось вернуть типы подарочных карт'}, status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mintGiftCard(request):
    try:
        amount = request.data.get('amount')
        cardTypeId = request.data.get('cardTypeId')
        if not cardTypeId:
            return Response({'error': 'Укажите тип покупаемой карты'}, status=400)
        if not amount:
            return Response({'error': 'Укажите номинал покупаемой карты'}, status=400)
        
        giftCardType = GiftCardType.objects.filter(pk=cardTypeId).first()
        if not giftCardType:
            return Response({'error': 'Данный тип карты не найден'}, status=400)
        amount = int(amount)
        if amount not in giftCardType.amountVariants:
            return Response({'error': 'Такой номинал подарочной карты не поддерживается'}, status=400)

        settings = getServerSettings()
        if not settings:
            return Response({'error': SETTINGS_ERROR}, status=400)
        createdGiftCard = GiftCard.objects.create(
            balance=amount,
            user=request.user,
            cardType=giftCardType,
        )
        
        params = {
            'userName': settings["sber_api_login"],
            'password': settings["sber_api_password"],
            'currency': 643,
            'orderNumber': createdGiftCard.promocode,
            'description': f'Оплата подарочной карты в магазине Персона. Промокод карты: {createdGiftCard.promocode}'[:512],
            'amount': int(amount*100),
            'returnUrl': 'personashop://gift-card-pay-success',
            'failUrl': 'personashop://gift-card-pay-failed'
        }

        registerUrl = f'{settings["sber_api_url"]}/register.do'
        data = requests.get(registerUrl, params=params, verify=False).json()
        if data.get('orderId'):
            createdGiftCard.orderSberId = data['orderId']
            createdGiftCard.save()
            checkGiftCardOrderStatusAndUpdateStateTask.apply_async(
                args=[data['orderId']],
                countdown=settings["sber_api_payment_time_limit"]
            )
        return Response({
            **data,
            'orderIdInBackend': createdGiftCard.promocode
        })
    except:
        return Response({'error': 'Не удалось вернуть типы подарочных карт'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateAllOwnGiftCardStatuses(request):
    try:
        orders = GiftCard.objects.filter(user=request.user)
        for order in orders:
            checkGiftCardOrderStatusAndUpdateStateTask(order.orderSberId)
        return Response({'success': 'Операция прошла успешно'})
    except Exception as e:
        print(e)
        return Response({'error': 'Неизвестная ошибка'}, status=400)
