from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api.models.user import User
from api.utils import connectToPersonaDB
from celery import shared_task


@shared_task
def syncUsersTask():
    try:
        connection = connectToPersonaDB()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT `User_ID`,`Language`,`Password`,`Login`,`FullName`,`Email`,`Birthday`,`PermissionGroup_ID` FROM User")
            for row in cursor:
                userId = int(row[0])
                lang = row[1]
                md5pass = row[2]
                phoneNumber = row[3]
                fullName = row[4]
                email = row[5]
                dob = row[6]
                is_staff = str(row[7]) == '3'

                name_parts = str(fullName).split(' ')
                firstName = name_parts[0] if len(name_parts) > 0 else ""
                lastName = name_parts[1] if len(name_parts) > 1 else ""

                userData = {
                    'userId': userId,
                    'language': lang or '',
                    'md5password': md5pass,
                    'phoneNumber': phoneNumber,
                    'firstName': firstName,
                    'lastName': lastName,
                    'email': email or '',
                    'birthday': dob or '',
                    'is_staff': is_staff,
                    'is_superuser': is_staff,
                }

                User.objects.update_or_create(**userData)

        return Response({'success': 'Синхронизация прошла успешно'})
    except:
        return Response({'error': 'Ошибка синхронизации'})
    

@api_view(['POST'])
@permission_classes([IsAdminUser])
def syncUsers(request):
    syncUsersTask.delay()
    return Response({'success': 'Синхронизация пользователей была запущенна'})