from django.db import models
from environment import SMS_RU_API_KEY, SBER_API_URL, SBER_API_LOGIN, SBER_API_PASSWORD

class ServerSettings(models.Model):
    sms_ru_api_key = models.CharField(default=SMS_RU_API_KEY, max_length=1000)
    sber_api_url = models.CharField(default=SBER_API_URL, max_length=1000)
    sber_api_login = models.CharField(default=SBER_API_LOGIN, max_length=1000)
    sber_api_password = models.CharField(default=SBER_API_PASSWORD, max_length=1000)
    delivery_cost_in_rub = models.PositiveIntegerField(blank=False)

    isActive = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Настройка сервера'
        verbose_name_plural = 'Настройки сервера'

    def __str__(self):
        return f"{self.pk} - active: [{'x' if self.isActive else ' '}]"
