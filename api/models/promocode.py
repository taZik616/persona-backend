from django.db import models


class Promocode(models.Model):
    code = models.CharField(max_length=60, unique=True, verbose_name='Код')
    benefit = models.JSONField(help_text='''
{<br>
    "discountPercent": 30,<br>
    # Если вы укажете значение discountPercent, то discountSum будет использован как максимальное значение скидки.<br>
    "discountSum": 5000,<br>
    # Порог при котором скидка начинает действовать<br>
    "startSumForDiscountSum": 50000<br>
}
''')
    productFilters = models.JSONField(help_text='''
# Здесь указываются фильтры, которые определят какие товары будут участвовать в промокоде.<br>
{<br>
    "subcategoryIds": ["ID", "ID"], # На товары каких-либо подкатегорий.<br>
    "categoryId": "ID", # На товары какой-либо категории.<br>
    "productIds": ["ID", "ID"], # На определенные товары.<br>
    "brandIds": ["ID", "ID"], # На товары какого-либо бренда.<br>
    "gender": "men" | "women",<br>
    "priceGroup": "Распродажа 30%" # На товары какой-либо группы цен.<br>
}<br>
null - значит промокод действует на все товары
''', null=True, blank=True)
    endDate = models.DateField(null=True, blank=True, help_text='''
Метка времени до которого промокод будет активен
''', verbose_name='Преимущества')

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'

    def __str__(self):
        discountPercent = self.benefit['discountPercent'] if self.benefit.get(
            'discountPercent') else 'Не указанна'
        discountSum = f"{self.benefit['discountSum']} ₽" if self.benefit.get(
            'discountSum') else 'Скидку определяют только проценты'
        return f"Код: {self.code}, Скидка в процентах: {discountPercent}, Скидка в рублях: {discountSum}"
