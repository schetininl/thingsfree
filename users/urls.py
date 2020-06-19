from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import PhoneVerificationViewSet, TokenObtainPairView

router = DefaultRouter()
router.register('phone', PhoneVerificationViewSet, basename='phone')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
]
