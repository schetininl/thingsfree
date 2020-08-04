from django.shortcuts import get_object_or_404
from django.shortcuts import render

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from rest_framework import filters, mixins, viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser,MultiPartParser,FormParser,JSONParser
from rest_framework import filters, mixins, viewsets,serializers, status
from rest_framework.response import Response #!
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import ValidationError

from . import responses
from . import permissions as offer_permissions
from .serializers import OfferClosedSerializer, OfferNotClosedSerializer, OfferCategorySerializer, OfferPhotoSerializer, OfferNotClosedSerializerModeration
from .models import OfferCategory, Offer, OfferPhoto
from users.models import User
#from .serializers import RegionSerializer, CitySerializer
#from cities.models import City, Region




class OfferViewSet(ModelViewSet):
    #queryset = Offer.objects.filter(is_closed=False)
    permission_classes = [ offer_permissions.IsOwnerOrReadOnly, ]
    pagination_class = LimitOffsetPagination
    #serializer_class = OfferNotClosedSerializer
    #filter_backends = [filters.OrderingFilter]
    ordering_fields = ['pub_date',]

    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['pub_date',]
    filterset_fields = ['category','city','is_service' ]

    def get_serializer_class(self):      
        if self.request.user.is_staff:
       # if offer_permissions.IsAdmin:    
            return OfferNotClosedSerializerModeration
        return OfferNotClosedSerializer

    def get_queryset(self): 
        #permission_classes = [ offer_permissions.IsAdmin, ] 
         
        if self.request.user.is_staff:
        #if offer_permissions.IsAdmin: #не работает не знаю почему...
            return Offer.objects.filter(is_closed=False)
        return Offer.objects.filter(is_closed=False,moderation_statuses= "APPROVED")


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
      
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            if request.data.get("description") is None:            
                return responses.INVALID_OFFER_DESCRIPTION
            elif request.data.get("title") is None:                
                return responses.INVALID_OFFER_TITLE 
            elif request.data.get("category") is None:                
                return responses.INVALID_OFFER_CATEGORY     
            return responses.OFFER_SAVING_ERROR
                  
                    
        except Exception:
            return responses.OFFER_SAVING_ERROR # возможно не нужен (избыточен) и его може можно удалить?
          
        self.perform_create(serializer)

        return responses.create_response(
               201100,
               serializer.data,
           )    

    
    def list(self, request, *args, **kwargs):
        
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = super().get_paginated_response(serializer.data)

            return responses.create_response(
                200000,
                paginated_response.data
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
    permission_classes = [offer_permissions.IsAdminOrReadOnly,  ]
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
    permission_classes = [ offer_permissions.IsOfferAuthorOrReadOnly, ] 
    serializer_class = OfferPhotoSerializer  

    def get_queryset(self):
        offer = get_object_or_404(Offer, id=self.kwargs.get("offer_id"))
        photos = OfferPhoto.objects.filter(offer=offer)
        return photos

    
    def perform_create(self, serializer):  
        offer = get_object_or_404(Offer, id=self.kwargs.get("offer_id"))
        author = offer.author
        self.check_object_permissions(self.request, offer)

        if OfferPhoto.objects.filter(offer = offer).count() >= 5: 
       
            raise serializers.ValidationError(
                detail="limit photos",
                code=status.HTTP_400_BAD_REQUEST
            )    

        serializer.save(offer_id=offer.id)
