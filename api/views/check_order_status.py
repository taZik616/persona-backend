import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.common_error_messages import SETTINGS_ERROR
from api.utils import getServerSettings
from celery import shared_task
from api.models import Order

@shared_task
def checkOrderStatusAndUpdateStateTask(orderId):
    '''
    `orderId` - идентификатор который выдает сбербанк
    '''
    try:
        if not orderId:
            return {'error': 'Вы не указали идентификатор заказа'}

        settings = getServerSettings()
        if not settings:
            return {'error': SETTINGS_ERROR}

        url = f'{settings["sber_api_url"]}/getOrderStatus.do'
        params = {
            'userName': settings['sber_api_login'],
            'password': settings['sber_api_password'],
            'orderId': orderId
        }

        response = requests.get(url, params=params, verify=False)
        data = response.json()
        if data.get('OrderStatus') != None and data.get('OrderNumber') != None:
            order = Order.objects.filter(orderId=data['OrderNumber']).first()
            order.status = 'NotPaid'
            match data['OrderStatus']:
                case 2:
                    order.status = 'AlreadyPaid'
                case 3:
                    order.status = 'AuthorizationDenied'
                case 4:
                    order.status = 'AuthorizationDenied'
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
        return Response(data, status=400)
    else:
        return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateAllOwnOrdersStatus(request):
    try:
        orders = Order.objects.filter(user=request.user)
        for order in orders:
            checkOrderStatusAndUpdateStateTask(order.orderSberId)
        return Response({'success': 'Операция прошла успешно'}, status=400)
    except Exception as e:
        print(e)
        return Response({'error': 'Неизвестная ошибка'}, status=400)
