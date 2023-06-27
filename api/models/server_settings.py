from django.db import models

from environment import (
    SBER_API_LOGIN,
    SBER_API_PASSWORD,
    SBER_API_PAYMENT_TIME_LIMIT,
    SBER_API_URL,
    SMS_RU_API_KEY,
)


class ServerSettings(models.Model):
    sms_ru_api_key = models.CharField(default=SMS_RU_API_KEY, max_length=1000)
    sber_api_url = models.CharField(default=SBER_API_URL, max_length=1000)
    sber_api_login = models.CharField(default=SBER_API_LOGIN, max_length=1000)
    sber_api_password = models.CharField(
        default=SBER_API_PASSWORD, max_length=1000)
    delivery_cost_in_rub = models.PositiveIntegerField()
    sber_api_payment_time_limit_sec = models.PositiveIntegerField(
        default=SBER_API_PAYMENT_TIME_LIMIT, verbose_name='Время через которое запускается авто-проверка статуса созданного заказа')

    isActive = models.BooleanField(default=True, verbose_name='Активированные(да/нет)')

    class Meta:
        verbose_name = 'Настройка сервера'
        verbose_name_plural = 'Настройки сервера'

    def __str__(self):
        return f"{self.pk} - active: [{'x' if self.isActive else ' '}]"
