from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('phone', views.PhoneVerificationViewSet, basename='phone')
router.register(
    r'users/(?P<user_id>.+)',
    views.FollowingViewSet,
    basename='following'
)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', views.TokenObtainPairView.as_view()),
    path('token/refresh/', views.TokenRefreshView.as_view()),
    path('social/providers/', views.get_social_providers),
    path('social/convert_token/', views.convert_social_token),
]
