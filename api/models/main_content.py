from django.db import models
from api.constants import GENDERS, MAIN_CONTENTS


class MainContent(models.Model):
    """
    Модель которая отвечает за содержание главной страницы приложения
    """
    type = models.CharField(
        max_length=100, choices=MAIN_CONTENTS, default='', blank=False, null=False)
    gender = models.CharField(
        max_length=10, choices=GENDERS, default='', blank=False, null=False)
    bannerCardUri = models.CharField(
        default='', max_length=200, blank=True, null=True)
    title = models.CharField(
        default='', max_length=100, blank=True, null=True)
    items = models.CharField(default='', max_length=500)

    class Meta:
        verbose_name = 'Элемент содержания'
        verbose_name_plural = 'Содержание главной страницы'

    def __str__(self):
        return self.NameSlider
