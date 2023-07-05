from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api.common_error_messages import SETTINGS_ERROR
from api.models import ServerSettings
from api.utils import connectToPersonaDB


@api_view(['POST'])
@permission_classes([IsAdminUser])
def syncSizesPage(request):
    try:
        settings = ServerSettings.objects.filter(isActive=True).first()
        if not settings:
            return Response({'error': SETTINGS_ERROR})
        connection = connectToPersonaDB()
        with connection.cursor() as cursor:
            cursor.execute('SELECT text FROM Message2000 WHERE Message_ID = 9')
            sizes = cursor.fetchone()
            text = sizes[0]
            settings.sizesPageContent = text
            settings.save()
            return Response({'success': 'Синхронизация страницы размеров прошла успешно'})
    except Exception as e:
        print(e)
        return Response({'error': 'При синхронизации размеров со сторонней БД произошла ошибка'}, status=400)
