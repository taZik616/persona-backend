from django.db import models
from api.models.user import User
from django.dispatch import receiver
from django.db.models.signals import pre_delete, pre_save
from os import path, remove
from django.core.files.storage import default_storage
import random
import string


class GiftCardType(models.Model):
    initialCardAmount = models.PositiveIntegerField(primary_key=True, unique=True)
    image = models.ImageField(default=None, upload_to='gift-card/')
    title = models.CharField(max_length=2000)
    description = models.CharField(max_length=2000)

    class Meta:
        verbose_name = 'Тип подарочных карт'
        verbose_name_plural = '4.2. Типы подарочных карт'

    def __str__(self):
        return f"{self.pk}. \"{self.title}\", начальный номинал: {self.initialCardAmount} ₽"

@receiver(pre_delete, sender=GiftCardType)
def deleteImage(sender, instance, **kwargs):
    if instance.image:
        image_path = instance.image.path
        if path.isfile(image_path):
            remove(image_path)


@receiver(pre_save, sender=GiftCardType)
def deletePreviousImage(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        if old_instance.image != instance.image:
            if old_instance.image:
                default_storage.delete(old_instance.image.path)

def generateGiftCardId():
    chars = string.ascii_letters + string.digits
    return 'gift-card-' + ''.join(random.choice(chars) for _ in range(20))

class GiftCard(models.Model):
    giftCardId = models.CharField(default=generateGiftCardId, max_length=32, unique=True, db_index=True, primary_key=True)
    balance = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    cardType = models.ForeignKey(
        GiftCardType, on_delete=models.SET_NULL, blank=True, null=True
    )
    promocode = models.UUIDField(blank=True)
    isActive = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Подарочная карта'
        verbose_name_plural = '4.1. Подарочные карты'

    def __str__(self):
        return f"Promocode: {self.promocode}, balance: {self.balance}, level: {self.cardType.title if self.cardType else '?'}, phone: {self.user.phoneNumber if self.user else '?'}"
