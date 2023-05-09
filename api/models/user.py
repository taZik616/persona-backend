from typing import Any, MutableMapping, Optional, Tuple
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


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
    userId = models.AutoField(primary_key=True, unique=True)
    language = models.CharField(default='Russian', max_length=15)
    phoneNumber = models.CharField(max_length=15, default='', unique=True)
    firstName = models.CharField(max_length=40, blank=True)
    lastName = models.CharField(max_length=40, blank=True)
    email = models.EmailField(max_length=200, blank=True)
    birthday = models.CharField(max_length=120, default='', blank=True)
    favorites = models.TextField(default='', max_length=9000, blank=True)
    isPhoneNumberVerified = models.BooleanField(default=False, blank=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

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
