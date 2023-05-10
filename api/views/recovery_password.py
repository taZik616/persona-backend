from rest_framework.response import Response
from rest_framework.decorators import api_view

from api.models.user import User
from api.utils import validateAndFormatPhoneNumber, sendCodeToPhone, specialEncodePassword, connectToPersonaDB
from django.core.cache import cache


@api_view(['POST'])
def RecoveryPasswordSendView(request):
    try:
        phoneNumber = request.data.get('phoneNumber')
        if not phoneNumber:
            return Response({
                "error": "Чтобы начать восстановление, вам нужно указать номер телефона"
            }, status=400)
        res = validateAndFormatPhoneNumber(phoneNumber)
        if not res['success']:
            return Response({"error": res.get('error')}, status=400)

        formattedPhoneNumber = res.get('formattedPhoneNumber')
        try:
            User.objects.get(phoneNumber=formattedPhoneNumber)
        except:
            return Response({"error": 'Такого пользователя не существует'})

        codeSendRes = sendCodeToPhone(formattedPhoneNumber)

        code = codeSendRes.get('code')
        if not code:
            return codeSendRes

        cache.set(
            f'rec-pass-{formattedPhoneNumber}',
            {'codeMd5': specialEncodePassword(code)},
            timeout=60*60*6  # 6 часов на восстановление
        )

        return Response({
            "success": f"На номер '{formattedPhoneNumber}' был отправлен пароль, у вас есть 6 часов чтобы подтвердить восстановление"
        })
    except:
        return Response({
            "error": "Не удалось запустить восстановление"
        }, status=400)


@api_view(['POST'])
def RecoveryPasswordConfirmView(request):
    try:
        phoneNumber = request.data.get('phoneNumber')
        supposedCode = request.data.get('supposedCode')
        newPassword = request.data.get('newPassword')

        if not phoneNumber or not supposedCode or not newPassword:
            return Response({
                "error": "Для завершения восстановления, вам нужно указать: номер телефона, предполагаемый код, новый пароль"
            }, status=400)

        res = validateAndFormatPhoneNumber(phoneNumber)
        if not res['success']:
            return Response({"error": res.get('error')}, status=400)

        formattedPhoneNumber = res.get('formattedPhoneNumber')
        user: User
        try:
            user = User.objects.get(phoneNumber=formattedPhoneNumber)
        except:
            return Response({"error": 'Такого пользователя не существует'})

        state = cache.get(f'rec-pass-{formattedPhoneNumber}')
        if state is None:
            return Response({"error": 'Сначала нужно начать процесс восстановления'}, status=400)

        codeMd5 = state.get('codeMd5')
        supposedCodeMd5 = specialEncodePassword(supposedCode)

        if codeMd5 == supposedCodeMd5:
            connection = connectToPersonaDB()
            user.set_password(newPassword)

            with connection.cursor() as cursor:
                cursor.execute(
                    f"UPDATE `User` SET `Password` = '{user.password}' WHERE `User_ID` = {user.userId};"
                )
                user.save()
                cache.delete(f'rec-pass-{formattedPhoneNumber}')
                return Response({"success": 'Пароль аккаунта был успешно восстановлен'}, status=400)
        else:
            return Response({"error": 'Введен не правильный код подтверждения'}, status=400)
    except:
        return Response({"error": 'Не удалось завершить восстановление пароля'}, status=400)
