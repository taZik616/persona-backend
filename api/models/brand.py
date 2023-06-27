from os import path, remove

from django.core.files.storage import default_storage
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from api.constants import BRAND_GENDERS


class Brand(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False, verbose_name='Название бренда')
    brandId = models.CharField(
        default='', max_length=20, blank=False, null=False, primary_key=True, verbose_name='Бренд')
    logo = models.ImageField(
        upload_to='brands/', default=None, blank=True, null=True, verbose_name='Логотип')
    description = models.CharField(default='', max_length=5000, blank=True, verbose_name='Описание')
    keywords = models.TextField(default='', max_length=20000, blank=True, verbose_name='Ключевые слова')
    gender = models.CharField(
        choices=BRAND_GENDERS, max_length=20, null=True, verbose_name='Пол')
    isTop = models.BooleanField(default=False, blank=True, verbose_name='Топовый(да/нет)')

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'

    def __str__(self):
        return f"{self.name} - {self.brandId}"


@receiver(pre_delete, sender=Brand)
def deleteImage(sender, instance, **kwargs):
    if instance.logo:
        image_path = instance.logo.path
        if path.isfile(image_path):
            remove(image_path)


@receiver(pre_save, sender=Brand)
def deletePreviousImage(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        if old_instance.logo != instance.logo:
            if old_instance.logo:
                default_storage.delete(old_instance.logo.path)
