
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", "USER")
        extra_fields.setdefault("is_approved", False)

        return super().create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("is_approved", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return super().create_superuser(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )


class CustomUser(AbstractUser):

    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('USER', 'User'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='USER'
    )

    is_approved = models.BooleanField(
        default=False
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.username
