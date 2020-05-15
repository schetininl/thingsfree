from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):

    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer.'
                    'Letters, digits and @/./+/-/_ only.'),
        validators=[UnicodeUsernameValidator()],
        blank=True
    )
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
