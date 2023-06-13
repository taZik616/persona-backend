import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.common_error_messages import SETTINGS_ERROR
from api.utils import getServerSettings

@api_view(['POST'])
def checkOrderStatus(request):
    try:
        orderId = request.data.get('orderId')
        if not orderId:
            return Response({'error': 'Вы не указали идентификатор заказа'})

        settings = getServerSettings()
        if not settings:
            return Response({'error': SETTINGS_ERROR}, status=400)

        url = f'{settings["sber_api_url"]}/getOrderStatus.do'
        params = {
            'userName': settings['sber_api_login'],
            'password': settings['sber_api_password'],
            'orderId': orderId
        }

        response = requests.get(url, params=params, verify=False)
        data = response.json()
        return Response(data)
    except Exception as e:
        print(e)
        return Response({'error': 'Не удалось узнать статус заказа'}, status=400)