from django.db import models


class Color(models.Model):
    name = models.CharField(
        max_length=1000, blank=False, null=False, unique=True, primary_key=True
    )
    hex = models.CharField(max_length=9)

    class Meta:
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'

    def __str__(self):
        return f"{self.name} - {self.hex}"
