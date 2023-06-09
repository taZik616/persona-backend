from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from api.models import DiscountCard, DiscountCardLevel, User
from api.utils import connectToPersonaDB, validateAndFormatPhoneNumber
from celery import shared_task


@shared_task
def syncDiscountCardsTask():
    try:
        connection = connectToPersonaDB()
        with connection.cursor() as cursor:
            discountCardLevelFields = 'discount_cards_Name, discount_cards_Priority, Value'
            cursor.execute(
                f'SELECT {discountCardLevelFields} FROM Classificator_discount_cards WHERE Checked = 1'
            )
            discountCardLevels = cursor.fetchall()

            for discountCardLevel in discountCardLevels:
                percent, level, value = discountCardLevel
                try:
                    percent = int(percent)
                    level = int(level)
                    DiscountCardLevel.objects.update_or_create(
                        level=level,
                        defaults={
                            'discountPercent': percent,
                            'purchaseThreshold': 100000*level if level > 1 else 0,
                            'encodedValue': value
                        }
                    )
                except ValueError:
                    print("Ошибка преобразования строки в целое число")

            discountCardFields = 'Phone, Card_code, Card_type'
            cursor.execute(
                f"SELECT {discountCardFields} FROM User_Discounts WHERE Phone LIKE '7%' AND LENGTH(Phone) > 6"
            )
            discountCards = cursor.fetchall()

            for discountCard in discountCards:
                phoneNumber, cardCode, cardTypeEncoded = discountCard
                if phoneNumber.startswith('7'):
                    phoneNumber=f"+{phoneNumber}"

                res = validateAndFormatPhoneNumber(phoneNumber)
                if not res['success']:
                    continue
                formattedPhoneNumber: str = res.get('formattedPhoneNumber')

                user = User.objects.filter(phoneNumber=formattedPhoneNumber).first()
                if user:
                    cardLevel = DiscountCardLevel.objects.filter(encodedValue=cardTypeEncoded).first()
                    if cardLevel:
                        try:
                            DiscountCard.objects.update_or_create(
                                user=user,
                                defaults={
                                    'cardCode': cardCode,
                                    'cardLevel': cardLevel,
                                    'purchaseTotal': cardLevel.purchaseThreshold
                                }
                            )
                        except Exception as e:
                            print(e)
    except Exception as e:
        print(e)
    
@api_view(['POST'])
@permission_classes([IsAdminUser])
def syncDiscountCards(request):
    syncDiscountCardsTask.delay()
    return Response({'success': 'Синхронизация скидочных карт была запущенна'})
