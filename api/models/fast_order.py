import random
import string

from django.db import models

from api.constants import ORDER_STATUS


def generateOrderId():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(30))


class FastOrder(models.Model):
    # Не AutoField потому что будет конфликт(в сбребанке) с заказами модели Order
    orderId = models.CharField(
        default=generateOrderId, max_length=32, unique=True, db_index=True, primary_key=True, verbose_name='Идентификатор')
    orderSberId = models.CharField(max_length=255, verbose_name='Идентификатор сбербанка')
    phoneNumber = models.CharField(max_length=18, verbose_name='Номер телефона')
    name = models.CharField(max_length=40, verbose_name='Название')
    address = models.CharField(max_length=1500, verbose_name='Адрес')
    productLegacyInfo = models.JSONField(blank=False, verbose_name='Инфо о товарах в устаревшем виде')
    productInfo = models.JSONField(blank=False, verbose_name='Инфо о товарах')
    status = models.CharField(max_length=50, choices=ORDER_STATUS, verbose_name='Статус')

    class Meta:
        verbose_name = 'Быстрый заказ'
        verbose_name_plural = 'Быстрые заказы'

    def __str__(self):
        return f"{self.orderId} - Телефон: {self.phoneNumber} - Статус: {self.status}"
