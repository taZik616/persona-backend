from django.db import models
from api.constants import GENDERS


class Brand(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    brandId = models.CharField(
        default='', max_length=20, blank=False, null=False, primary_key=True)
    logoUrl = models.CharField(
        default='', max_length=500, blank=False, null=False)
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
