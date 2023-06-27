from django.db import models

from api.constants import GENDERS, MAIN_CONTENTS


class MainSwiperImage(models.Model):
    imageUrl = models.URLField(verbose_name='URL картинки')
    # Здесь будут фильтры для просмотра товаров соответствующих картинке
    productFilters = models.JSONField(verbose_name='Фильтры товаров')

    class Meta:
        verbose_name = 'Картинка для свайпера'
        verbose_name_plural = '2.2. Картинки для свайпера'


def defaultItemsValue():
    return []


class OtherContent(models.Model):
    type = models.CharField(max_length=200, choices=MAIN_CONTENTS, verbose_name='Тип содержания')
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    # Я без понятия что еще юзать если не джсон
    items = models.JSONField(default=defaultItemsValue, help_text='''
queryFilters - параметры для дополнительной настройки запроса product
Например: search, isNew, subcategoryId, categoryId, brand__brandId ...<br><br>
# BrandsList 'Список брендов'<br>
{
  brandId: string,
  queryFilters?: { ... }
}<br><br>
# BrandsSwiper 'Свайпер брендов'<br>
{
  brandId: string,
  imgUri: string,
  queryFilters?: { ... }
}<br><br>
# CategoriesList 'Список категорий'<br>
{
  categoryId: number,
  queryFilters?: { ... }
}<br><br>
# FashionList 'Список образов'<br>
{
  productIds: string[],
  imgUri: string
}<br><br>
# FashionSwiper 'Свайпер образов'<br>
{
  productIds: string[],
  imgUri: string
}
''', verbose_name='Список элементов')

    class Meta:
        verbose_name = 'Доп. контент'
        verbose_name_plural = '2.3. Доп. контент'


class MainContent(models.Model):
    """
    Модель которая отвечает за содержание главной страницы приложения
    """
    mainSwiperImages = models.ManyToManyField(MainSwiperImage, verbose_name='Картинки главного свайпера')
    bannerCard = models.URLField(verbose_name='Картинка баннера')
    otherContent = models.ManyToManyField(OtherContent, verbose_name='Дополнительный контент')
    gender = models.CharField(
        max_length=10, choices=GENDERS, default='', blank=False, null=False, verbose_name='Пол'
    )
    isInactive = models.BooleanField(default=False, verbose_name='Выключить')

    class Meta:
        verbose_name = 'Содержание главной страницы'
        verbose_name_plural = '2.1. Содержание главных страниц'

    def __str__(self):
        return f'{self.pk} - {self.gender}, active: [{" " if self.isInactive else "x"}]'
