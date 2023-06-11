from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Promocode, User
from datetime import date
from api.serializers import PromocodeSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkPromocode(request):
    try:
        promocode = request.data.get('promocode')
        if not promocode:
            return Response({'error': 'Вы не указали промо-код'}, status=400)

        promocode = Promocode.objects.filter(code=promocode).first()
        if not promocode:
            return Response({'error': 'Такого промо-кода нету'}, status=400)

        curDate = date.today()
        if promocode.endDate and not promocode.endDate >= curDate:
            return Response({'error': 'Промокод уже не действителен'}, status=400)

        user: User = request.user
        if user.usedPromocodes.filter(code=promocode.code).exists():
            return Response({'error': 'Вы уже использовали этот промокод'}, status=400)
        
        return Response({
            'success': 'Промокод прошел проверку',
            'data': PromocodeSerializer(promocode).data
        })
    except Exception as e:
        print(str(e))
        return Response({'error': 'Ошибка сервера, попробуйте позже'}, status=400)
