from django.db import models

from api.constants import ORDER_STATUS
from api.models.promocode import Promocode
from api.models.user import User


class Order(models.Model):
    orderId = models.AutoField(unique=True, db_index=True, primary_key=True)
    orderSberId = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=1500)
    productsLegacyInfo = models.JSONField(blank=False)
    productsInfo = models.JSONField(blank=False)
    costumerInfo = models.JSONField(blank=False)
    usedPromocode = models.ForeignKey(
        Promocode, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=50, choices=ORDER_STATUS)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"{self.orderId} - {self.user.phoneNumber if self.user else 'Удаленный пользователь'} - Статус: {self.status}"
