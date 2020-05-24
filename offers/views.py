from django.shortcuts import render

from django.contrib.auth import get_user_model
from rest_framework import filters, mixins, viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from .serializers import OfferClosedSerializer, OfferNotClosedSerializer, OfferCategorySerializer, RegionSerializer, CitySerializer

from .models import OfferCategory, Offer, Region, City

User = get_user_model()




class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.filter(is_closed=False)
    permission_classes = [permissions.AllowAny,]
    serializer_class = OfferNotClosedSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['pub_date',]

class OfferCategoryViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin):

    queryset = OfferCategory.objects.all()
    serializer_class = OfferCategorySerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny, ]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class RegionViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin):

    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny, ]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]    


class CityViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin):

    queryset = City.objects.all()
    serializer_class = CitySerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny, ]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]