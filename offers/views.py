from django.shortcuts import get_object_or_404
from django.shortcuts import render

from django.contrib.auth import get_user_model

from rest_framework import filters, mixins, viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser,MultiPartParser,FormParser,JSONParser
from rest_framework import filters, mixins, viewsets,serializers, status

from .serializers import OfferClosedSerializer, OfferNotClosedSerializer, OfferCategorySerializer, OfferPhotoSerializer
from .models import OfferCategory, Offer, OfferPhoto
from users.models import User
#from .serializers import RegionSerializer, CitySerializer
#from cities.models import City, Region



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


#class RegionViewSet(viewsets.GenericViewSet,
#                      mixins.ListModelMixin,
#                      mixins.CreateModelMixin,
#                      mixins.DestroyModelMixin):

#    queryset = Region.objects.all()
#    serializer_class = RegionSerializer
#    lookup_field = 'id'
#    permission_classes = [permissions.AllowAny, ]
#    filter_backends = [filters.SearchFilter]
#    search_fields = ['name', ]    


#class CityViewSet(viewsets.GenericViewSet,
#                      mixins.ListModelMixin,
#                      mixins.CreateModelMixin,
#                      mixins.DestroyModelMixin):

#    queryset = City.objects.all()
#    serializer_class = CitySerializer
#    lookup_field = 'id'
#    permission_classes = [permissions.AllowAny, ]
#    filter_backends = [filters.SearchFilter]
#    search_fields = ['name', ]

#class OfferPhotoViewSet(viewsets.GenericViewSet,
#                      mixins.ListModelMixin,
#                      mixins.CreateModelMixin,
#                      mixins.DestroyModelMixin):
#    queryset = OfferPhoto.objects.all()
#    serializer_class = OfferPhotoSerializer 
#    lookup_field = 'id'
#    permission_classes = [permissions.AllowAny, ]
#    parser_classes = (MultiPartParser,FormParser,JSONParser,)

class OfferPhotoViewSet(ModelViewSet):
    queryset = OfferPhoto.objects.all()
    permission_classes = [permissions.AllowAny,]
    serializer_class = OfferPhotoSerializer  
    
    def perform_create(self, serializer):  
        if OfferPhoto.objects.filter(offer = self.request.data.get('offer')).count() >= 5: 
       
            raise serializers.ValidationError(
                detail="limit photos",
                code=status.HTTP_400_BAD_REQUEST
            )    
        serializer.save(offer_id=self.request.data.get('offer'))
