from django.db import models
from enumfields import EnumField
from enum import Enum

from .brand import Brand


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
    brand = models.OneToOneField(
        Brand, on_delete=models.PROTECT, blank=True, null=True)

    collection = models.CharField(
        default='', max_length=1000, blank=False, null=False)

    priceGroup = models.CharField(default='', max_length=200)
    previewImages = models.CharField(
        default='', max_length=3000, blank=False, null=False)

    isAvailable = models.BooleanField(blank=False, null=False)
    isNew = models.BooleanField(blank=False, null=False)
    lastUpdate = models.DateTimeField()

    def __str__(self):
        return f"{self.productName} - {self.productId}"

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = '1. Продукты'


class ProductCharacteristic(models.Model):
    id = models.CharField(
        unique=True, max_length=100, primary_key=True, blank=False, null=False)
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    # Производитель
    manufacturer = models.CharField(default='', max_length=1000)
    country = models.CharField(default='', max_length=100)
    # Подклад - материалы швейного производства, используемые для изготовления подкладки одежды
    podklad = models.CharField(default='', max_length=100)
    sostav = models.CharField(default='', max_length=300)

    def __str__(self):
        return f"{self.product.productName}. manufacturer: {self.manufacturer}, \
            country: {self.country}, podklad: {self.podklad}, sostav: {self.sostav}"

    class Meta:
        verbose_name = 'Характеристика продукта'
        verbose_name_plural = '3. Характеристики продуктов'


class ProductVariant(models.Model):
    size = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    # На всякий случай, это id товара с такими характеристиками в БД
    uniqueId = models.CharField(
        unique=True, max_length=100, primary_key=True, blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.productName}. size: {self.size}, \
            color: {self.color}, idForBuying: {self.uniqueId}"

    class Meta:
        verbose_name = 'Вариант продукта'
        verbose_name_plural = '2. Варианты продукта'
