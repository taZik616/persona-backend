from django.db import models

from api.constants import ORDER_STATUS
from api.models.promocode import Promocode
from api.models.user import User


class Order(models.Model):
    orderId = models.AutoField(unique=True, db_index=True, primary_key=True, verbose_name='Идентификатор')
    orderSberId = models.CharField(max_length=255, blank=True, verbose_name='Идентификатор сбербанка')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    address = models.CharField(max_length=1500, verbose_name='Адрес')
    productsLegacyInfo = models.JSONField(blank=False, verbose_name='Инфо о товарах в устаревшем виде')
    productsInfo = models.JSONField(blank=False, verbose_name='Инфо о товарах')
    costumerInfo = models.JSONField(blank=False, verbose_name='Инфо о пользователе')
    usedPromocode = models.ForeignKey(
        Promocode, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Промокод')
    status = models.CharField(max_length=50, choices=ORDER_STATUS, verbose_name='Статус')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"{self.orderId} - {self.user.phoneNumber if self.user else 'Удаленный пользователь'} - Статус: {self.status}"
