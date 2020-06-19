from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('phone', views.PhoneVerificationViewSet, basename='phone')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', views.TokenObtainPairView.as_view()),
    path('token/refresh/', views.TokenRefreshView.as_view()),
    path('social/', include('rest_framework_social_oauth2.urls')),
]
