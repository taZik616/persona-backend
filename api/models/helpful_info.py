from django.db import models

from api.constants import HELPFUL_INFO_KEYS


class HelpfulInfo(models.Model):
    key = models.CharField(max_length=200, choices=HELPFUL_INFO_KEYS, primary_key=True, unique=True, verbose_name='Ключ контента')
    markdownContent = models.TextField(help_text='''
MarkDown используется для улучшения вида страниц с информацией, работает как уникальная разметка, которая может обрабатываться как в web среде, так и в мобильных приложениях
''', verbose_name='Контент в MarkDown формате')
    
    def __str__(self):
        return self.key

    class Meta:
        verbose_name = 'Полезная информация'
        verbose_name_plural = 'Отдел полезной информации'
