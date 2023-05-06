from django.db import models


class AnotherImage(models.Model):
    imageId = models.CharField(default='', max_length=100)
    name = models.CharField(default='', max_length=100, blank=True)
    image = models.ImageField(default=None, upload_to='another_images/')

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'

    def __str__(self):
        return self.name if self.name else self.imageId
