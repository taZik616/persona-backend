from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.models.user import User
from api.utils import connectToPersonaDB


class DiscountCardLevel(models.Model):
    level = models.IntegerField(primary_key=True, unique=True, verbose_name='Уровень')
    purchaseThreshold = models.PositiveIntegerField(help_text='''
Это значение определяет минимальную сумму покупок, необходимую для перехода карты на данный уровень.<br>
Уровень карты будет установлен на основе максимального уровня, если сумма покупок соответствует этому порогу.
''', unique=True, verbose_name='Необходимая сумма покупок')
    discountPercent = models.IntegerField(verbose_name='Процент скидки')
    encodedValue = models.CharField(max_length=100, verbose_name='Закодированное значение')

    class Meta:
        verbose_name = 'Уровень скидочных карт'
        verbose_name_plural = '3.2. Уровни скидочных карт'

    def __str__(self):
        return f"{self.level} уровень - {self.discountPercent}%"


class DiscountCard(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, verbose_name='Пользователь')
    cardCode = models.CharField(max_length=100, unique=True, verbose_name='Код карты')
    cardLevel = models.ForeignKey(
        DiscountCardLevel, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Уровень карты'
    )
    purchaseTotal = models.IntegerField(default=0, verbose_name='Сумма покупок')

    class Meta:
        verbose_name = 'Скидочная карта'
        verbose_name_plural = '3.1. Скидочные карты'

    def __str__(self):
        return f"user: {self.user.phoneNumber}, purchase total: {self.purchaseTotal}, level: {self.cardLevel.level if self.cardLevel else '?'}, code: {self.cardCode}"


@receiver(post_save, sender=DiscountCard)
def assign_card_level(sender, instance, **kwargs):
    cardLevel = DiscountCardLevel.objects.filter(
        purchaseThreshold__lte=instance.purchaseTotal
    ).order_by('-level').first()
    card = DiscountCard.objects.filter(pk=instance.pk)
    if card:
        card.update(cardLevel=cardLevel)
        card = card.first()
        connection = connectToPersonaDB()
        with connection.cursor() as cursor:
            phone = card.user.phoneNumber.replace('+', '')

            cursor.execute(
                f"UPDATE User_Discounts SET Card_type = '{cardLevel.encodedValue}' WHERE Phone = '{phone}';")
            cursor.connection.commit()
