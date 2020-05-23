from django.contrib import admin

from .models import OfferCategory


class OfferCategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name")
    empty_value_display = "-пусто-"


admin.site.register(OfferCategory, OfferCategoryAdmin)
