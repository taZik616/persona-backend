from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from api.common_error_messages import ONLY_ADMIN


class SizesPageView(APIView):
    def get(self, request):
        try:
            text = cache.get('sizes-page', '')
            return Response({'page': text})
        except:
            return Response({'error': 'Не удалось вернуть страницу размеров'}, status=400)

    def put(self, request):
        if not request.user.is_superuser:
            return Response({'error': ONLY_ADMIN}, status=400)
        try:
            text = request.data.get('text')
            cache.set('sizes-page', text)
            return Response({'success': 'Вы успешно изменили страницу размеров'})
        except:
            return Response({'error': 'Не удалось изменить страницу размеров'}, status=400)
