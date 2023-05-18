from django.db import models
from api.constants import GENDERS, MAIN_CONTENTS
from django.db import models


class MainSwiperImage(models.Model):
    imageUrl = models.URLField()
    # Здесь будут фильтры для просмотра товаров соответствующих картинке
    productFilters = models.JSONField()

    class Meta:
        verbose_name = 'Картинка для свайпера'
        verbose_name_plural = '2.2. Картинки для свайпера'


class OtherContent(models.Model):
    type = models.CharField(max_length=200, choices=MAIN_CONTENTS)
    title = models.CharField(max_length=100)
    # Я без понятия что еще юзать если не джсон
    items = models.JSONField(help_text='''
# BrandsList 'Список брендов'<br>
{
  id: string
  brandId: number
  imgUri: string
  logoUri: string
}<br><br>
# BrandsSwiper 'Свайпер брендов'<br>
{
  id: string
  brandId: number
  imgUri: string
}<br><br>
# CategoriesList 'Список категорий'<br>
{
  id: string
  categoryId: number
  imgUri: string
  name: string
}<br><br>
# FashionList 'Список товаров'<br>
{
  id: string
  productIds: number[]
  imgUri: string
}<br><br>
# FashionSwiper 'Свайпер товаров'<br>
{
  id: string
  productIds: number[]
  imgUri: string
}
''')

    class Meta:
        verbose_name = 'Доп. контент'
        verbose_name_plural = '2.3. Доп. контент'


class MainContent(models.Model):
    """
    Модель которая отвечает за содержание главной страницы приложения
    """
    mainSwiperImages = models.ManyToManyField(MainSwiperImage)
    bannerCard = models.URLField()
    otherContent = models.ManyToManyField(OtherContent)
    gender = models.CharField(
        max_length=10, choices=GENDERS, default='', blank=False, null=False
    )
    isInactive = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Содержание главной страницы'
        verbose_name_plural = '2.1. Содержание главных страниц'

    def __str__(self):
        return f'{self.pk} - {self.gender}, active: [{" " if self.isInactive else "x"}]'
