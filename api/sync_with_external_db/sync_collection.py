from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api.models import Collection
from api.utils import connectToPersonaDB


@api_view(['POST'])
@permission_classes([IsAdminUser])
def syncCurrentSeasonCollection(request):
    try:
        connection = connectToPersonaDB()
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT Subdivision_Name FROM Subdivision WHERE Subdivision_ID = 333')
            collection = cursor.fetchone()

            collectionName = collection[0]
            Collection.objects.update_or_create(
                collectionId='333',
                defaults={'name': collectionName}
            )
            return Response({'success': 'Синхронизация коллекции текущего сезона прошла успешно'})
    except Exception as e:
        print(e)
        return Response({'error': 'При синхронизации коллекции текущего сезона со сторонней БД произошла ошибка'}, status=400)
