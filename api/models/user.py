from typing import Any

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from .product import Product, ProductVariant
from .promocode import Promocode


class UserManager(BaseUserManager):
    def create_user(self, password=None, md5password=None, **extra_fields):
        phoneNumber = extra_fields.get('phoneNumber')

        if not password and not md5password:
            raise ValueError('The password field must be set')
        if not phoneNumber:
            raise ValueError('The Email field must be set')
        user = self.model(**extra_fields)

        if md5password:
            user.password = md5password
        else:
            user.set_password(password)
        user.save()
        return user

    def update_or_create(self, **kwargs: Any):
        userId = kwargs.get('userId')
        try:
            user = self.get(userId=userId)
            if user:
                return self.update(**kwargs)
            else:
                raise Exception('user not found')
        except:
            return self.create_user(**kwargs)

    def update(self, md5password=None, **kwargs: Any) -> int:
        if md5password:
            return super().update(**kwargs, password=md5password)
        else:
            return super().update(**kwargs)

    def create_superuser(self, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(**extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    userId = models.AutoField(primary_key=True, unique=True, verbose_name='Идентификатор')
    language = models.CharField(default='Russian', max_length=15, verbose_name='Язык')
    phoneNumber = models.CharField(max_length=15, default='', unique=True, verbose_name='Номер телефона')
    firstName = models.CharField(max_length=40, blank=True, verbose_name='Имя')
    lastName = models.CharField(max_length=40, blank=True, verbose_name='Фамилия')
    email = models.EmailField(max_length=200, blank=True, verbose_name='e-mail')
    birthday = models.CharField(max_length=120, default='', blank=True, verbose_name='Дата рождения')
    isPhoneNumberVerified = models.BooleanField(default=False, blank=True, verbose_name='Подтвержденный телефон(да/нет)')
    usedPromocodes = models.ManyToManyField(Promocode, blank=True, verbose_name='Использованные промокоды')

    subEmail = models.BooleanField(default=False, blank=True, verbose_name='Подписка на e-mail')
    subSms = models.BooleanField(default=False, blank=True, verbose_name='Подписка на sms')
    subPush = models.BooleanField(default=False, blank=True, verbose_name='Подписка на push-уведомления')

    is_staff = models.BooleanField(default=False, verbose_name='Персонал')
    is_superuser = models.BooleanField(default=False, verbose_name='Супер пользователь')

    USERNAME_FIELD = 'phoneNumber'

    objects = UserManager()

    class Meta:
        verbose_name = 'Аккаунт'
        verbose_name_plural = 'Аккаунты'

    def __str__(self):
        if self.firstName or self.lastName:
            return f"{self.phoneNumber}, {self.firstName} {self.lastName}"
        else:
            return self.phoneNumber


class BasketItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name='Товар')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, verbose_name='Вариант')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='basketItems', verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'

    def __str__(self):
        return f"user: '{self.user.phoneNumber}'. {self.product.productName} - {self.product.productId}, {self.variant.uniqueId}"


class FavoriteItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favoriteItems', verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Элемент избранного'
        verbose_name_plural = 'Элементы избранного'

    def __str__(self):
        return f"user: '{self.user.phoneNumber}'. {self.product.productName} - {self.product.productId}"
