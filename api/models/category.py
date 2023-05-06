from django.db import models
from enumfields import EnumField
from enum import Enum


class Level(Enum):
    CATEGORY = 1
    SUBCATEGORY = 2


class Category(models.Model):
    categoryId = models.CharField(default='', max_length=50)
    name = models.CharField(default='', max_length=100)
    description = models.CharField(default='', max_length=5000, blank=True)
    keywords = models.TextField(default='', max_length=20000, blank=True)
    logoUrl = models.CharField(default='', max_length=500)
    gender = models.CharField(default='', max_length=10)
    level = EnumField(Level)
    # Subdivision_ID = models.CharField(default='', max_length=50)
    # Catalogue_ID = models.CharField(default='', max_length=50)
    # Parent_Sub_ID = models.CharField(default='', max_length=50)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.categoryName
