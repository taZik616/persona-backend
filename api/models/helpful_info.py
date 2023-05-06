from django.db import models


class HelpfulInfo(models.Model):
    exchange_and_return = models.TextField(
        default='0', max_length=20000, blank=False, null=False)
    terms_of_sale = models.TextField(
        default='0', max_length=20000, blank=False, null=False)
    privacy_policy = models.TextField(
        default='0', max_length=20000, blank=False, null=False)
    payment = models.TextField(
        default='0', max_length=20000, blank=False, null=False)
    contacts = models.TextField(
        default='0', max_length=20000, blank=False, null=False)
    delivery = models.TextField(
        default='0', max_length=20000, blank=False, null=False)

    def __str__(self):
        return f"Полезная информация - {self.pk}"

    class Meta:
        verbose_name = 'Полезная информация'
        verbose_name_plural = 'Полезная информация'
