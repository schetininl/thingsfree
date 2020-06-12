import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.core import validators
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import pre_save

from cities.models import City#, Region
from users.models import User


class OfferCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name='Наименование', max_length=50)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class CloseReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name='Причина закрытия')

    class Meta:
        verbose_name = 'Причина закрытия'

    def __str__(self):
        return self.name


class Offer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    MODERATION_STATUSES_CHOICES = (
        ('ON_MODERATION', 'На модерации'),
        ('APPROVED', 'Одобрено'),
        ('REFUSED', 'Отклонено'),
    )

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=280)
    category = models.ForeignKey(
        OfferCategory, on_delete=models.CASCADE, related_name="offers")
    is_service = models.BooleanField()
    is_used = models.BooleanField()
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, blank=True, null=True, related_name="offers")
    pub_date = models.DateField(
        verbose_name='Дата публикации', auto_now_add=True)
    is_private = models.BooleanField(
        verbose_name='Приватное/общедоступное предложение')
    moderation_statuses = models.CharField(verbose_name='Статус модерации', max_length=50, 
        choices=MODERATION_STATUSES_CHOICES, default='ON_MODERATION')
    is_closed = models.BooleanField(
        verbose_name='Открытое/закрытое предложение')
    close_reason = models.ForeignKey(CloseReason, 
        on_delete=models.PROTECT, blank=True, null=True, related_name="offers") 

    class Meta:
        verbose_name = 'Предложение'
        verbose_name_plural = 'Предложения'

#@receiver(pre_save, sender=Offer)
#def offer_pre_save(sender, instance, **kwargs):
#    if instance.photos > 5: #тут переделать  instance.offer.photos + уточнить почему нет поля photo у offer 
#        raise ValidationError("Вы не можете загрузить больше фотографий!")
                

# class OfferPhoto(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     offer = models.ForeignKey(
#         Offer, on_delete=models.CASCADE, related_name="photo")
#     # поле для ссылки на изображение:
#     link = models.ImageField(upload_to='offers/', blank=True, null=True)

#     class Meta:
#         verbose_name = 'Фотография предложения'
#         verbose_name_plural = 'Фотографии предложения'

def nameFile(instance, filename):
    return '/'.join(['photos', str(instance.link), filename])

class OfferPhoto(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="photos")
    # поле для ссылки на изображение:
    link = models.ImageField(upload_to=nameFile, blank=True, null=True)

    def save(self,*args,**kwargs):
        
        if OfferPhoto.objects.filter(offer= self.offer.id).count()>=5:
            return 
        super(OfferPhoto,self).save(*args,**kwargs)
            
    
    class Meta:
        verbose_name = 'Фотография предложения'
        verbose_name_plural = 'Фотографии предложения'        