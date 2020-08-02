from django.shortcuts import get_object_or_404
from django.shortcuts import render

from django.contrib.auth import get_user_model

from rest_framework import filters, mixins, viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser,MultiPartParser,FormParser,JSONParser
from rest_framework import filters, mixins, viewsets,serializers, status
from rest_framework.response import Response #!

from . import responses
from . import permissions as offer_permissions
from .serializers import OfferClosedSerializer, OfferNotClosedSerializer, OfferCategorySerializer, OfferPhotoSerializer
from .models import OfferCategory, Offer, OfferPhoto
from users.models import User
#from .serializers import RegionSerializer, CitySerializer
#from cities.models import City, Region



class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.filter(is_closed=False)
    permission_classes = [permissions.AllowAny, offer_permissions.IsOwnerOrReadOnly, ]
    serializer_class = OfferNotClosedSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['pub_date',]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def list(self, request, *args, **kwargs):
        
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return responses.create_response(
                200000,
                serializer.data
                )
        serializer = self.get_serializer(queryset, many=True)
        return  responses.create_response(
                200000,
                serializer.data 
            )

    def retrieve(self, request, *args, **kwargs): #чтобы единичный пост с этими полями показывал
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return responses.create_response(
                200000,
                serializer.data 
            )

 

class OfferCategoryViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin):

    queryset = OfferCategory.objects.all()
    serializer_class = OfferCategorySerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny, offer_permissions.IsAdminOrReadOnly,  ]
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

    #queryset = OfferPhoto.objects.all()
    permission_classes = [permissions.AllowAny, offer_permissions.IsOwnerOrReadOnly, ]
    serializer_class = OfferPhotoSerializer  

    def get_queryset(self):
        offer = get_object_or_404(Offer, id=self.kwargs.get("offer_id"))
        photos = OfferPhoto.objects.filter(offer=offer)
        return photos

    
    def perform_create(self, serializer):  
        offer = get_object_or_404(Offer, id=self.kwargs.get("offer_id"))

        if OfferPhoto.objects.filter(offer = offer).count() >= 5: 
       
            raise serializers.ValidationError(
                detail="limit photos",
                code=status.HTTP_400_BAD_REQUEST
            )    
#        serializer.save(offer_id=self.request.data.get('offer'))
        serializer.save(offer_id=offer.id)
