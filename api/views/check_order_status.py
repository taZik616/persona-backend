import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.common_error_messages import SETTINGS_ERROR
from api.utils import getServerSettings
from celery import shared_task
from api.models import Order, FastOrder

@shared_task
def checkOrderStatusAndUpdateStateTask(orderId, isFastOrder = False):
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
                order = FastOrder.objects.filter(orderId=data['orderNumber']).first()
            else:
                order = Order.objects.filter(orderId=data['orderNumber']).first()
            if not order:
                return {'error': 'Не удалось найти заказ'}
            if order.status != 'Delivery' and order.status != 'Received':
                match data['orderStatus']:
                    case 2:
                        if not isFastOrder:
                            if order.usedPromocode:
                                order.user.usedPromocodes.add(order.usedPromocode)
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
        for order in orders:
            data = checkOrderStatusAndUpdateStateTask(order.orderSberId)
            if data.get('error'):
                checkOrderStatusAndUpdateStateTask(order.orderSberId, True)
        return Response({'success': 'Операция прошла успешно'})
    except Exception as e:
        print(e)
        return Response({'error': 'Неизвестная ошибка'}, status=400)
