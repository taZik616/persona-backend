from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view

from api.utils import validateAndFormatPhoneNumber


@ratelimit(key='ip', rate='16/h', block=False)
@api_view(['POST'])
def LoginView(request):
    """Для того чтобы получить токен нужны поля `username` и `password`"""
    is_blocked = getattr(request, 'limited', False)
    if is_blocked:
        return Response({'error': 'Вы превысили лимит запросов на вход, повторите через час'}, status=429)

    phoneNumber = request.data.get('username')

    res = validateAndFormatPhoneNumber(phoneNumber)
    if not res['success']:
        return Response({"error": res.get('error')})

    try:
        formattedPhoneNumber = res.get('formattedPhoneNumber')

        serializer = ObtainAuthToken.serializer_class(
            data={
                'username':  formattedPhoneNumber,
                'password': request.data.get('password')
            }, context={'request': request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Ну если пользователь смог залогиниться после регистрации,
        # то это значит он получил код подтверждения 💯
        if not user.isPhoneNumberVerified:
            user.isPhoneNumberVerified = True
            user.save()

        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'created': created})
    except:
        return Response({"error": 'Не удалось разрешить доступ'})
