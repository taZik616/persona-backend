from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view
from api.models import DiscountCard, DiscountCardLevel

from api.utils import validateAndFormatPhoneNumber, randomCardCode, connectToPersonaDB
import uuid

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
            discountCard = DiscountCard.objects.filter(user=user).exists()
            if not discountCard:
                while True:
                    code = randomCardCode()
                    if not DiscountCard.objects.filter(cardCode=code).exists():
                        try:
                            cardLevel = DiscountCardLevel.objects.filter(level=1).first()

                            if not cardLevel:
                                break
                            DiscountCard.objects.create(user=user, cardCode=code, cardLevel=cardLevel)
                            connection = connectToPersonaDB()
                            with connection.cursor() as cursor:
                                phone = user.phoneNumber.replace('+', '')
                                fullName = f"{user.firstName} {user.lastName}" if user.firstName and user.lastName else ""

                                fields = 'Phone, Name, Card_code, Card_type, 1C_ID'
                                values = f"'{phone}', '{fullName}', '{code}', '{cardLevel.encodedValue}', '{str(uuid.uuid4())}'"
                                QUERY = f"INSERT INTO User_Discounts ({fields}) VALUES ({values});"

                                cursor.execute(QUERY)
                                cursor.connection.commit()
                            break
                        except Exception as e:
                            print(e)
                            break

            user.isPhoneNumberVerified = True
            user.save()

        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'created': created})
    except:
        return Response({"error": 'Не удалось разрешить доступ'}, status=400)
