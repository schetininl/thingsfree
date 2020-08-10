from django.contrib import admin

from .models import Offer, OfferCategory, OfferPhoto


class OfferAdmin(admin.ModelAdmin):
    list_display = ("pk", "author", "title", "description", "category", "is_service",
                    "is_used", "city", "pub_date", "is_private", "moderation_statuses",
                    "is_closed", "close_reason")
    empty_value_display = "-пусто-"


class OfferCategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name")
    empty_value_display = "-пусто-"


class OfferPhotoAdmin(admin.ModelAdmin):
    list_display = ("pk", "offer", "link")
    empty_value_display = "-пусто-"


admin.site.register(OfferPhoto, OfferPhotoAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(OfferCategory, OfferCategoryAdmin)
