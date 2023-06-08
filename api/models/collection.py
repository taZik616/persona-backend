from django.db import models


class Collection(models.Model):
    collectionId = models.CharField(
        max_length=100, blank=False,
        null=False, primary_key=True,
        unique=True
    )
    name = models.CharField(max_length=1000, blank=False, null=False)

    class Meta:
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'

    def __str__(self):
        return f"{self.name} - {self.collectionId}"
