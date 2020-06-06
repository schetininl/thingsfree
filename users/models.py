import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from cities.models import City


class User(AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = PhoneNumberField(
        _('phone'),
        unique=True,
        error_messages={
            'unique': _('A user with that phone already exists.')
        },
        blank=True
    )
    avatar = models.CharField(
        _('photo'),
        max_length=200,
        blank=True
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='users'
    )

    @classmethod
    def phone_is_used(cls, phone_number):
        return cls.objects.filter(phone_number=phone_number).exists()

    def __str__(self):
        return self.username


class TypeOfContact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=50)

    class Meta:
        verbose_name = _('Type of contact')
        verbose_name_plural = _('Types of contact')

    def __str__(self):
        return self.name


class UserContact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contact_info'
    )
    type = models.ForeignKey(
        TypeOfContact,
        on_delete=models.CASCADE,
        related_name='contact_info'
    )
    text = models.TextField(_('text'))

    class Meta:
        verbose_name = _('User contact')
        verbose_name_plural = _('User contacts')
