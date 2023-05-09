from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from api.utils import connectToPersonaDB
from api.models import User


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ChangePasswordView(request):
    """Для того чтобы получить токен нужны поля `username` и `password`"""
    password = request.data.get('password')
    newPassword = request.data.get('newPassword')
    try:
        user: User = request.user

        if not user.check_password(password):
            return Response({'error': 'Пароль от аккаунта и введенный не совпадают'}, status=400)

        user.set_password(newPassword)
        hashedPassword = user.password

        connection = connectToPersonaDB()
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE `User` SET `Password` = '{hashedPassword}' WHERE `User_ID` = {user.userId};"
            )
            # Это не просто так тут стоит, set_password не сохраняет изменения экземпляра
            user.save()
            return Response({'success': 'Пароль успешно изменен!'}, status=400)
    except:
        return Response({"error": 'Не удалось сменить пароль'}, status=400)
