from os import path, remove

from django.core.files.storage import default_storage
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django_enumfield.enum import Enum, EnumField

from .product import Product


class CategoryLevel(Enum):
    CATEGORY = 1
    SUBCATEGORY = 2


class Category(models.Model):
    categoryId = models.AutoField(primary_key=True, unique=True, verbose_name='Идентификатор')
    parentId = models.CharField(default='', max_length=200, verbose_name='Родительский')
    name = models.CharField(default='', max_length=100, verbose_name='Название')
    description = models.CharField(default='', max_length=5000, blank=True, verbose_name='Описание')
    keywords = models.TextField(default='', max_length=50000, blank=True, verbose_name='Ключевые слова')
    gender = models.CharField(default='', max_length=10, verbose_name='Пол')
    level = EnumField(CategoryLevel)
    # С этого продукта будет вытянута картинка для демонстрации подкатегории
    subcategoryPreviewProduct = models.ForeignKey(
        Product, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Товар для демонстрации категории'
    )
    # Эта картинка будет относиться к демонстрации категории
    categoryPreviewImage = models.ImageField(
        default=None, upload_to='category-images/', blank=True, null=True, verbose_name='Картинка для категории'
    )
    checked = models.BooleanField(blank=False, null=False, verbose_name='Показывать пользователям(да/нет)')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


@receiver(pre_delete, sender=Category)
def deleteImage(sender, instance, **kwargs):
    if instance.image:
        image_path = instance.categoryPreviewImage.path
        if path.isfile(image_path):
            remove(image_path)


@receiver(pre_save, sender=Category)
def deletePreviousImage(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        if old_instance.categoryPreviewImage != instance.categoryPreviewImage:
            if old_instance.categoryPreviewImage:
                default_storage.delete(old_instance.categoryPreviewImage.path)
