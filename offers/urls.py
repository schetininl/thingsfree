from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OfferCategoryViewSet, OfferViewSet #, RegionViewSet, CityViewSet

router = DefaultRouter()
router.register('offers', OfferViewSet, basename='offers')
router.register('categories', OfferCategoryViewSet, basename='categories')
#router.register('regions', RegionViewSet, basename='regions')
#router.register('cities', CityViewSet, basename='cities')


urlpatterns = [
    path('', include(router.urls))

]