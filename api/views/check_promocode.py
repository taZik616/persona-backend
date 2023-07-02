from datetime import date

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import Promocode, User
from api.serializers import PromocodeSerializer


def checkPromocode(promocode: str, user: User):
    try:
        if not promocode:
            return {'error': 'Вы не указали промо-код'}

        promocode = Promocode.objects.filter(code=promocode).first()
        if not promocode:
            return {'error': 'Такого промо-кода нету'}

        curDate = date.today()
        if promocode.endDate and not promocode.endDate >= curDate:
            return {'error': 'Промокод уже не действителен'}

        if user.usedPromocodes.filter(code=promocode.code).exists():
            return {'error': 'Вы уже использовали этот промокод'}
        
        if user.hasFirstBuyInApp and promocode.onlyFirstBuyInAppPromo:
            return {'error': 'Промокод работает только на первую покупку в приложении'}

        return {
            'success': 'Промокод прошел проверку',
            'data': PromocodeSerializer(promocode).data
        }
    except Exception as e:
        print(str(e))
        return {'error': 'Ошибка сервера, попробуйте позже'}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkPromocodeView(request):
    promocode = request.data.get('promocode', '')
    data = checkPromocode(promocode, request.user)

    if data.get('error'):
        return Response(data, status=400)
    else:
        return Response(data)
