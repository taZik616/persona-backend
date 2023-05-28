from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from api.utils import connectToPersonaDB
from django.core.cache import cache


@api_view(['POST'])
@permission_classes([IsAdminUser])
def syncSizesPage(request):
    try:
        connection = connectToPersonaDB()
        with connection.cursor() as cursor:
            cursor.execute('SELECT text FROM Message2000 WHERE Message_ID = 9')
            sizes = cursor.fetchone()
            text = sizes[0]
            cache.set('sizes-page', text)
            return Response({'success': 'Синхронизация размеров прошла успешно'})
    except Exception as e:
        print(e)
        return Response({'error': 'При синхронизации размеров со сторонней БД произошла ошибка'}, status=400)
