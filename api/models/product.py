from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from .brand import Brand
from os import path, remove


class Product(models.Model):
    productId = models.CharField(
        unique=True, max_length=100, primary_key=True, blank=False, null=False)
    subcategoryId = models.CharField(
        default='', max_length=20, blank=False, null=False)
    categoryId = models.CharField(
        default='', max_length=20, blank=False, null=False)

    productName = models.CharField(default='', max_length=300)
    description = models.CharField(default='', max_length=2000)

    keywords = models.CharField(default='', max_length=2000)
    price = models.FloatField(default=0.0, blank=False, null=False)
    brand = models.ForeignKey(
        Brand, on_delete=models.PROTECT, blank=True, null=True)

    collection = models.CharField(
        default='', max_length=1000, blank=False, null=False)

    priceGroup = models.CharField(default='', max_length=200)
    previewImages = models.CharField(
        default='', max_length=3000, blank=False, null=False)

    isAvailable = models.BooleanField(blank=False, null=False)
    isNew = models.BooleanField(blank=False, null=False)
    lastUpdate = models.DateTimeField()

    # Производитель
    manufacturer = models.CharField(default='', max_length=1000)
    country = models.CharField(default='', max_length=100)
    # Подклад - материалы швейного производства, используемые для изготовления подкладки одежды
    podklad = models.CharField(default='', max_length=100)
    sostav = models.CharField(default='', max_length=300)

    onlyOneVariant = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.productName} - {self.productId}"

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = '1. Продукты'


class ProductVariant(models.Model):
    size = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    # На всякий случай, это id товара с такими характеристиками в БД
    uniqueId = models.CharField(
        unique=True, max_length=100, primary_key=True, blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField(default=0.0, blank=True, null=True)
    isAvailable = models.BooleanField(blank=True, null=True)

    class Meta:
        verbose_name = 'Вариант продукта'
        verbose_name_plural = '2. Варианты продукта'


class ProductImage(models.Model):
    imageId = models.CharField(default='', max_length=100)
    priority = models.IntegerField()
    compressedImage = models.ImageField(upload_to='multifields-compressed/')
    originalImage = models.ImageField(upload_to='multifields/')

    class Meta:
        verbose_name = 'Картинка товара'
        verbose_name_plural = '3. Картинки товаров'

    def __str__(self):
        return f'{self.imageId}'


@receiver(pre_delete, sender=ProductImage)
def deleteImages(sender, instance, **kwargs):
    if instance.compressedImage:
        image_path = instance.compressedImage.path
        if path.isfile(image_path):
            remove(image_path)
    if instance.originalImage:
        image_path = instance.originalImage.path
        if path.isfile(image_path):
            remove(image_path)
