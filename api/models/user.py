from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, phoneNumber, password=None, **extra_fields):
        if not phoneNumber:
            raise ValueError('The Email field must be set')
        phoneNumber = phoneNumber
        user = self.model(phoneNumber=phoneNumber, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phoneNumber, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phoneNumber, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    userId = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)

    language = models.CharField(default='Russian', max_length=15)
    # password = models.CharField(max_length=200, default='')
    phoneNumber = models.CharField(max_length=15, default='', unique=True)
    firstName = models.CharField(max_length=50, blank=True)
    lastName = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=200, blank=True)
    birthday = models.CharField(max_length=120, default='', blank=True)
    favorites = models.TextField(default='', max_length=9000, blank=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'phoneNumber'

    objects = UserManager()

    class Meta:
        verbose_name = 'Аккаунт'
        verbose_name_plural = 'Аккаунты'

    def __str__(self):
        if self.firstName or self.lastName:
            return f"{self.phoneNumber}, fullName: {self.firstName} {self.lastName}"
        else:
            return self.phoneNumber
