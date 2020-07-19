from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from social_django.models import Association, Nonce, UserSocialAuth
from .models import TypeOfContact, User, UserContact, SocialMedia


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('phone_number', 'first_name', 'last_name', 'email')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'email', 'phone_number', 'first_name',
                    'last_name', 'is_staff')


@admin.register(TypeOfContact)
class TypeOfContactAdmin(admin.ModelAdmin):
    fields = ('name',)


@admin.register(UserContact)
class UserContactAdmin(admin.ModelAdmin):
    fields = ('user', 'type', 'text')


@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    exclude = ('id',)


admin.site.unregister(Association)
admin.site.unregister(Nonce)
admin.site.unregister(UserSocialAuth)
