from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PhoneVerificationViewSet

router = DefaultRouter()
router.register('phone', PhoneVerificationViewSet, basename='phone')

urlpatterns = [
    path('', include(router.urls)),
]