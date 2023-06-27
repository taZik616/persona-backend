from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.common_error_messages import translateError
from api.serializers import UserInfoSerializer
from api.utils import connectToPersonaDB


class PersonalInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializedUser = UserInfoSerializer(request.user, many=False)
            return Response(serializedUser.data)
        except:
            return Response({'error': 'Не удалось вернуть данные'}, status=400)

    def put(self, request):
        try:
            serializedUser = UserInfoSerializer(
                data=request.data,
                partial=True
            )
            if serializedUser.is_valid():
                connection = connectToPersonaDB()
                with connection.cursor() as cursor:
                    preparedData = serializedUser._validated_data
                    user = serializedUser.update(request.user, preparedData)
                    if ' ' in user.firstName or ' ' in user.lastName:
                        return Response({'error': 'Имя и фамилия не должны содержать символы пробела'}, status=400)

                    fullName = f"{user.firstName} {user.lastName}"

                    cursor.execute(f"""
                    UPDATE `User` SET `FullName` = '{fullName}', `Email` = '{user.email if user.email else 'NULL'}', `Birthday` = '{user.birthday if user.birthday else 'NULL'}' WHERE `User_ID` = {user.userId};
                    """)

                    user.save()
                    return Response({'success': 'Пользователь был обновлен'})
            else:
                error = list(serializedUser.errors.values())[0][0]
                return Response({'error': translateError(error)}, status=400)
        except Exception as e:
            print(e)
            return Response({'error': 'Не удалось обновить пользователя'}, status=400)

    def delete(self, request):
        connection = connectToPersonaDB()

        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    f"DELETE FROM `User` WHERE `User`.`User_ID` = {request.user.userId};"
                )
                request.user.delete()
                return Response({
                    "success": f"Аккаунт({request.user.phoneNumber}) был успешно удален"
                })
            except:
                return Response({
                    "error": "Не удалось удалить аккаунт"
                }, status=400)
