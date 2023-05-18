from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.core.cache import cache


class HelpfulInfoView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request, infoName):
        try:
            content = cache.get(f'helpful-info-{infoName}')
            if not content:
                return Response({'error': 'Информация не найдена'})

            return Response({'data': content})
        except:
            return Response({'error': 'Информация не найдена'}, status=404)

    def put(self, request, infoName):
        try:
            content = request.data.get('content')
            if not content:
                return Response({'error': 'Укажите контент'}, status=400)
            cache.set(f'helpful-info-{infoName}', content)

            return Response({'success': f"Вы успешно добавили этот текст для '{infoName}'"})
        except:
            return Response({'error': f'Не удалось добавить контент'}, status=400)

    def delete(self, request, infoName):
        try:
            cache.delete(f'helpful-info-{infoName}')

            return Response({'success': f"Вы успешно удалили контент для '{infoName}'"})
        except:
            return Response({'error': f'Не удалось добавить контент'}, status=400)
