from django.db import models
from enumfields import EnumField
from enum import Enum


class CategoryLevel(Enum):
    CATEGORY = 1
    SUBCATEGORY = 2


class Category(models.Model):
    categoryId = models.AutoField(primary_key=True, unique=True)
    parentId = models.CharField(default='', max_length=200)
    name = models.CharField(default='', max_length=100)
    description = models.CharField(default='', max_length=5000, blank=True)
    keywords = models.TextField(default='', max_length=20000, blank=True)
    logoUrl = models.CharField(default='', max_length=500)
    gender = models.CharField(default='', max_length=10)
    level = EnumField(CategoryLevel)
    # Catalogue_ID = models.CharField(default='', max_length=50)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name
