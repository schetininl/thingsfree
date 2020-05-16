from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):

    phone_number = PhoneNumberField(
        _('phone'),
        unique=True,
        error_messages={
            'unique': _('A user with that phone already exists.')
        }
    )
    avatar = models.CharField(
        _('photo'),
        max_length=200,
        blank=True
    )

    USERNAME_FIELD = 'phone_number'
