from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OfferCategoryViewSet, OfferViewSet, OfferPhotoViewSet #, RegionViewSet, CityViewSet

router = DefaultRouter()
router.register('offers', OfferViewSet, basename='offers')
router.register('categories', OfferCategoryViewSet, basename='categories')
#router.register('regions', RegionViewSet, basename='regions')
#router.register('cities', CityViewSet, basename='cities')

#router.register('photos', OfferPhotoViewSet, basename='photos')

router.register(
    r'offers/(?P<offer_id>[-\d\w]+)/photos',
    OfferPhotoViewSet,
    basename='photos'
)


urlpatterns = [
    path('', include(router.urls))

]