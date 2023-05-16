from django.db import models
from api.constants import GENDERS
from django.dispatch import receiver
from django.db.models.signals import pre_delete, pre_save
from os import path, remove
from django.core.files.storage import default_storage


class Brand(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    brandId = models.CharField(
        default='', max_length=20, blank=False, null=False, primary_key=True)
    logo = models.ImageField(
        upload_to='brands/', default=None, blank=True, null=True)
    description = models.CharField(default='', max_length=5000, blank=True)
    keywords = models.TextField(default='', max_length=20000, blank=True)
    gender = models.CharField(
        choices=GENDERS, max_length=20, blank=False, null=False)
    isTop = models.BooleanField(default=False, blank=True)

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
            default_storage.delete(old_instance.logo.path)
