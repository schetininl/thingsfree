from django.contrib import admin

from .models import City, Region


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    fields = ('name', 'region')


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    fields = ('name', )