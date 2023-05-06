from django.db import models
from enumfields import EnumField
from enum import Enum

from .brand import Brand


class SizeCategories(Enum):
    SHOES = 1
    CLOTHES = 2
    PANTS = 3


class Size(models.Model):
    category = EnumField(SizeCategories, blank=False, null=False)
    # Например: "Ru", "Международный" ...
    type = models.CharField(default='', max_length=100,
                            blank=False, null=False)
    value = models.CharField(
        default='', max_length=100, blank=False, null=False)
    # Порядковый номер, чтобы иметь возможность создания таблицы
    ordinalIndex = models.IntegerField(default=0, blank=False, null=False)


class ProductCharacteristic(models.Model):
    # Производитель
    manufacturer = models.CharField(default='', max_length=1000)
    country = models.CharField(default='', max_length=100)
    # Подклад - материалы швейного производства, используемые для изготовления подкладки одежды
    podklad = models.CharField(default='', max_length=100)
    sostav = models.CharField(default='', max_length=300)
    color = models.CharField(default='', max_length=200)


class Product(models.Model):
    productId = models.CharField(
        unique=True, max_length=100, blank=False, null=False)
    subcategoryId = models.CharField(
        default='', max_length=20, blank=False, null=False)
    categoryId = models.CharField(
        default='', max_length=20, blank=False, null=False)

    productName = models.CharField(default='', max_length=300)
    description = models.CharField(default='', max_length=2000)

    article = models.CharField(default='', max_length=200)
    keywords = models.CharField(default='', max_length=2000)
    cost = models.FloatField(default=0.0, blank=False, null=False)
    brand = models.OneToOneField(Brand, on_delete=models.PROTECT)

    characteristic = models.OneToOneField(
        ProductCharacteristic, on_delete=models.CASCADE)
    size = models.OneToOneField(Size, on_delete=models.PROTECT)
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
