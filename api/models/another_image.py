from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete, pre_save
from os import path, remove
from django.core.files.storage import default_storage


class AnotherImage(models.Model):
    image = models.ImageField(default=None, upload_to='another-images/')

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'

    def __str__(self):
        return str(self.image).replace('another-images/', '')
    

@receiver(pre_delete, sender=AnotherImage)
def deleteImage(sender, instance, **kwargs):
    if instance.image:
        image_path = instance.image.path
        if path.isfile(image_path):
            remove(image_path)


@receiver(pre_save, sender=AnotherImage)
def deletePreviousImage(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        if old_instance.image != instance.image:
            if old_instance.image:
                default_storage.delete(old_instance.image.path)
