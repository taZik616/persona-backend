from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import HelpfulInfo


@api_view(['GET'])
def getHelpfulInfo(request, infoName):
    try:
        if not infoName:
            return Response({'error': 'Не указан нужный раздел'}, status=404)
        info = HelpfulInfo.objects.filter(key=infoName).first()
        if not info:
            return Response({'error': 'Информация не найдена'}, status=404)

        return Response({'data': info.markdownContent})
    except:
        return Response({'error': 'Неизвестная ошибка'}, status=404)
