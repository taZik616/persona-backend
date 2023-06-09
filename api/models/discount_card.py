from django.db import models
from api.models.user import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class DiscountCardLevel(models.Model):
    level = models.IntegerField(primary_key=True, unique=True)
    purchaseThreshold = models.PositiveIntegerField(help_text='''
Это значение определяет минимальную сумму покупок, необходимую для перехода карты на данный уровень.<br>
Уровень карты будет установлен на основе максимального уровня, если сумма покупок соответствует этому порогу.
''', unique=True)
    discountPercent = models.IntegerField()
    encodedValue = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Уровень скидочных карт'
        verbose_name_plural = '3.2. Уровни скидочных карт'

    def __str__(self):
        return f"{self.level} уровень - {self.discountPercent}%"


class DiscountCard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cardCode = models.CharField(max_length=100)
    cardLevel = models.ForeignKey(
        DiscountCardLevel, on_delete=models.SET_NULL, blank=True, null=True
    )
    purchaseTotal = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Скидочная карта'
        verbose_name_plural = '3.1. Скидочные карты'

    def __str__(self):
        return f"user: {self.user.phoneNumber}, purchase total: {self.purchaseTotal}, level: {self.cardLevel.level}, code: {self.cardCode}"

@receiver(post_save, sender=DiscountCard)
def assign_card_level(sender, instance, **kwargs):
    cardLevel = DiscountCardLevel.objects.filter(
        purchaseThreshold__lte=instance.purchaseTotal
    ).order_by('-level').first()
    DiscountCard.objects.filter(pk=instance.pk).update(cardLevel=cardLevel)