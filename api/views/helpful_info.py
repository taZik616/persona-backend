from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from api.common_error_messages import ONLY_ADMIN


class HelpfulInfoView(APIView):
    def get(self, request, infoName):
        try:
            content = cache.get(f'helpful-info')
            if not content or infoName not in content:
                return Response({'error': 'Информация не найдена'}, status=404)

            return Response({'data': content[infoName]})
        except:
            return Response({'error': 'Информация не найдена'}, status=404)

    def put(self, request, infoName):
        if not request.user.is_superuser:
            return Response({'error': ONLY_ADMIN}, status=400)
        try:
            content = request.data.get('content')
            if not content:
                return Response({'error': 'Укажите контент'}, status=400)
            if not infoName:
                return Response({'error': 'Укажите в строке запроса для чего данное описание'}, status=400)

            all_content = cache.get(f'helpful-info')
            if not all_content:
                all_content = {}

            all_content[infoName] = content
            cache.set(f'helpful-info', all_content)

            return Response({'success': f"Вы успешно добавили этот текст для '{infoName}'"})
        except:
            return Response({'error': f'Не удалось добавить контент'}, status=400)

    def delete(self, request, infoName):
        if not request.user.is_superuser:
            return Response({'error': ONLY_ADMIN}, status=400)
        try:
            content = cache.get(f'helpful-info')
            if not content or infoName not in content:
                return Response({'error': 'Информация не найдена'}, status=404)

            del content[infoName]
            cache.set(f'helpful-info', content)

            return Response({'success': f"Вы успешно удалили контент для '{infoName}'"})
        except:
            return Response({'error': f'Не удалось удалить контент'}, status=400)
