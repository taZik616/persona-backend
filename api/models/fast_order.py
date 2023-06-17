from django.db import models
from api.constants import ORDER_STATUS
import random
import string


def generateOrderId():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(30))

class FastOrder(models.Model):
    # Не AutoField потому что будет конфликт(в сбребанке) с заказами модели Order 
    orderId = models.CharField(default=generateOrderId, max_length=32, unique=True, db_index=True, primary_key=True)
    orderSberId = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=18)
    name = models.CharField(max_length=40)
    address = models.CharField(max_length=1500)
    productLegacyInfo = models.JSONField(blank=False)
    productInfo = models.JSONField(blank=False)
    status = models.CharField(max_length=50, choices=ORDER_STATUS)

    class Meta:
        verbose_name = 'Быстрый заказ'
        verbose_name_plural = 'Быстрые заказы'

    def __str__(self):
        return f"{self.orderId} - Телефон: {self.phoneNumber} - Статус: {self.status}"
