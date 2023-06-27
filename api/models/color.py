from django.db import models


class Color(models.Model):
    name = models.CharField(
        max_length=1000, blank=False, null=False, unique=True, primary_key=True, verbose_name='Название'
    )
    hex = models.CharField(max_length=9, verbose_name='Код цвета(hex)')

    class Meta:
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'

    def __str__(self):
        return f"{self.name} - {self.hex}"
