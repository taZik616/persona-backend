import random
import string
from array import array
from os import path, remove

from django.core.files.storage import default_storage
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from api.models.user import User


def defaultAmountVariants():
    return [5000, 10000, 50000]


def isArray(obj):
    return isinstance(obj, (list, tuple, array))


class GiftCardType(models.Model):
    image = models.ImageField(default=None, upload_to='gift-card/', verbose_name='Картинка')
    title = models.CharField(max_length=2000, verbose_name='Название')
    description = models.CharField(max_length=2000, verbose_name='Описание')
    amountVariants = models.JSONField(
        default=defaultAmountVariants,
        help_text='Тут мы указываем какие номиналы карт доступны для покупок', verbose_name='Варианты номинала'
    )

    class Meta:
        verbose_name = 'Тип подарочных карт'
        verbose_name_plural = '4.2. Типы подарочных карт'

    def __str__(self):
        nominals = ', '.join(str(item) for item in self.amountVariants) if isArray(
            self.amountVariants) else 'NULL'
        return f"{self.pk}. \"{self.title}\", возможные номиналы: {nominals} ₽"


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
    promocode = models.CharField(
        default=generateGiftCardId, max_length=32, unique=True, db_index=True, primary_key=True)
    balance = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cardType = models.ForeignKey(
        GiftCardType, on_delete=models.SET_NULL, blank=True, null=True
    )
    isActive = models.BooleanField(default=False)
    isBlocked = models.BooleanField(default=False)
    orderSberId = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Подарочная карта'
        verbose_name_plural = '4.1. Подарочные карты'

    def __str__(self):
        return f"Promocode: {self.promocode}, balance: {self.balance}, level: {self.cardType.title if self.cardType else '?'}, phone: {self.user.phoneNumber if self.user else '?'}"
