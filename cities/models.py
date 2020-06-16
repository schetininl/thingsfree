import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Region(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=50, unique=True)

    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')
        ordering = ('name',)

    def __str__(self):
        return self.name


class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=50)
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='cities'
    )

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
        ordering = ('name',)
        unique_together = (('name', 'region'),)

    def __str__(self):
        return self.name
