from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from api.models.user import User

from ..utils import connectToPersonaDB, validateAndFormatPhoneNumber, specialEncodePassword, ActionLimiter, sendCodeToPhone

INTERVAL = 60*60
registryLimiter = ActionLimiter('registry-', 6, INTERVAL, INTERVAL)


@api_view(['PUT'])
def RegistrySendCodeView(request):
    """
    Для регистрации необходимы поля `phoneNumber`
    Дополнительные поля: `firstName` и `lastName`

    Здесь мы создаем пользователя с паролем из звонка сервиса sms.ru
    """
    addressIP = request.META.get('REMOTE_ADDR')
    isBlocked = registryLimiter.getIsBlocked(addressIP)

    if isBlocked:
        return Response({'error': 'Вы превысили лимит запросов, повторите через час'}, status=429)

    phoneNumber = request.data.get('phoneNumber')

    res = validateAndFormatPhoneNumber(phoneNumber)
    if not res['success']:
        return Response({"error": res.get('error')}, status=400)

    formattedPhoneNumber:str = res.get('formattedPhoneNumber')
    firstName = request.data.get('firstName', '')
    lastName = request.data.get('lastName', '')

    connection = connectToPersonaDB()
    with connection.cursor() as cursor:
        try:
            isUserAlreadyExist = User.objects.filter(
                phoneNumber=formattedPhoneNumber).count() >= 1
            if isUserAlreadyExist:
                return Response({'error': 'Аккаунт с данным номером уже был создан'}, status=400)

            registryLimiter.increment(addressIP)
            codeSendRes = sendCodeToPhone(formattedPhoneNumber)

            code = codeSendRes.get('code')
            if not code:
                return codeSendRes

            md5password = specialEncodePassword(str(code))

            # Узнаем какой ID не занят
            cursor.execute("""
                SELECT MIN(User_ID) + 1 AS next_id
                FROM User
                WHERE (User_ID + 1) NOT IN (SELECT User_ID FROM User)
            """)
            res = cursor.fetchone()
            newUserId = res[0] if res[0] else 1

            user = User.objects.create_user(
                userId=newUserId,
                phoneNumber=formattedPhoneNumber,
                firstName=firstName,
                lastName=lastName,
                password=str(code)
            )

            nowDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fullName = f"{firstName} {lastName}" if firstName and lastName else ""

            form = 'User_ID, Password, PermissionGroup_ID, Checked, Language, Created, LastUpdated, Confirmed, RegistrationCode, Keyword, Login, Catalogue_ID, InsideAdminAccess, Auth_Hash, UserType, FullName, Email, Birthday, ncAttemptAuth, Account'
            values = f"'{user.userId}', '{md5password}', 2, 1, 'Russian', '{nowDate}', '{nowDate}', 0, '', NULL, '{formattedPhoneNumber.replace('+', '')}', 0, 0, NULL, 'normal', '{fullName}', NULL, NULL, 0, NULL"

            QUERY = f"INSERT User({form}) VALUES ({values});"

            cursor.execute(QUERY)
            cursor.connection.commit()

            return Response({
                "success": f"На номер был отправлен пароль",
                "formattedPhoneNumber": formattedPhoneNumber
            })
        except Exception as e:
            print(str(e))
            try:
                createdNowUser = User.objects.get(
                    phoneNumber=formattedPhoneNumber)
                createdNowUser.delete()
            except:
                pass
            return Response({
                "error": f"Ошибка сервера"
            }, status=400)

resendLimiter = ActionLimiter('registry-resend-code-', 1, 60*5, 60*5)

@api_view(['POST'])
def RegistryResendCodeView(request):
    """
    Повторная отправка кода по СМС
    """
    addressIP = request.META.get('REMOTE_ADDR')
    isBlocked = resendLimiter.getIsBlocked(addressIP)

    if isBlocked:
        return Response({'error': 'Вы превысили лимит, повторите через 5 минут'}, status=429)

    phoneNumber = request.data.get('phoneNumber')
    if not phoneNumber:
        return Response({"error": 'Укажите номер телефона'}, status=400)

    res = validateAndFormatPhoneNumber(phoneNumber)
    if not res['success']:
        return Response({"error": res.get('error')}, status=400)

    formattedPhoneNumber = res.get('formattedPhoneNumber')

    connection = connectToPersonaDB()
    with connection.cursor() as cursor:
        try:
            user: User = User.objects.filter(
                phoneNumber=formattedPhoneNumber
            ).first()
            if not user:
                return Response({'error': 'Аккаунт еще не был создан'}, status=400)
            if user.isPhoneNumberVerified:
                return Response({'error': 'Пользователь уже подтвердил свой номер'}, status=400)
            
            codeSendRes = sendCodeToPhone(formattedPhoneNumber)

            code = codeSendRes.get('code')
            if not code:
                return codeSendRes

            md5password = specialEncodePassword(str(code))

            user.password = md5password
            user.save()
            resendLimiter.increment(addressIP)

            cursor.execute(f"UPDATE User SET Password = '{md5password}' WHERE User_ID = '{user.userId}';")

            return Response({
                "success": "На номер был отправлен новый пароль",
                "formattedPhoneNumber": formattedPhoneNumber
            })
        except Exception as e:
            print(str(e))
            return Response({"error": f"Ошибка сервера" }, status=400)
