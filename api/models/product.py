from os import path, remove

from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .brand import Brand


class Product(models.Model):
    productId = models.CharField(
        db_index=True, unique=True,
        max_length=100, primary_key=True,
        blank=False, null=False, verbose_name='Идентификатор товара'
    )
    subcategoryId = models.CharField(
        default='', max_length=20, blank=False, null=False, verbose_name='Подкатегория(ID)')
    categoryId = models.CharField(
        default='', max_length=20, blank=False, null=False, verbose_name='Категория(ID)')

    productName = models.CharField(default='', max_length=300, verbose_name='Наименование товара')
    description = models.CharField(default='', max_length=2000, verbose_name='Описание')

    keywords = models.CharField(default='', max_length=2000, verbose_name='Ключевые слова')
    price = models.FloatField(default=0.0, blank=False, null=False, verbose_name='Цена')
    brand = models.ForeignKey(
        Brand, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Бренд')

    collection = models.CharField(
        default='', max_length=1000, blank=False, null=False, verbose_name='Коллекция')

    priceGroup = models.CharField(default='', max_length=200, verbose_name='Ценовая группа')
    discountPercent = models.IntegerField(default=0, verbose_name='Процент скидки')
    article = models.CharField(db_index=True, max_length=300, verbose_name='Артикул')

    isAvailable = models.BooleanField(blank=False, null=False, verbose_name='Доступен(да/нет)')
    isNew = models.BooleanField(blank=False, null=False, verbose_name='Новый(да/нет)')
    checked = models.BooleanField(blank=False, null=False, verbose_name='Показывать пользователям(да/нет)')
    lastUpdate = models.DateTimeField(verbose_name='Последнее обновление')

    # Производитель
    manufacturer = models.CharField(default='', max_length=1000, verbose_name='Производитель')
    country = models.CharField(default='', max_length=100, verbose_name='Страна')
    # Подклад - материалы швейного производства, используемые для изготовления подкладки одежды
    podklad = models.CharField(default='', max_length=100, verbose_name='Подклад')
    sostav = models.CharField(default='', max_length=300, verbose_name='Состав')

    onlyOneVariant = models.BooleanField(default=True, verbose_name='Только 1 вариант товара')


    def __str__(self):
        return f"{self.productName} - {self.productId}"

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = '1.1. Продукты'


class ProductVariant(models.Model):
    size = models.CharField(max_length=100, verbose_name='Размер')
    color = models.CharField(max_length=100, verbose_name='Цвет')
    # На всякий случай, это id товара с такими характеристиками в БД
    uniqueId = models.CharField(
        unique=True, max_length=100, primary_key=True, blank=False, null=False, verbose_name='Уникальный идентификатор')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    price = models.FloatField(default=0.0, blank=True, null=True, verbose_name='Цена')
    isAvailable = models.BooleanField(blank=True, null=True, verbose_name='Доступен(да/нет)')
    priceGroup = models.CharField(default='', max_length=200, verbose_name='Ценовая группа')
    discountPercent = models.IntegerField(default=0, verbose_name='Процент скидки')

    class Meta:
        verbose_name = 'Вариант продукта'
        verbose_name_plural = '1.2. Варианты продукта'


class ProductImage(models.Model):
    imageId = models.CharField(db_index=True, default='', max_length=100, verbose_name='Идентификатор')
    priority = models.IntegerField(verbose_name='Приоритет в порядке')
    compressedImage = models.ImageField(upload_to='multifields-compressed/', verbose_name='Сжатая картинка')
    originalImage = models.ImageField(upload_to='multifields/', verbose_name='Картинка')

    class Meta:
        verbose_name = 'Картинка товара'
        verbose_name_plural = '1.3. Картинки товаров'

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
