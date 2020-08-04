from rest_framework import serializers

from .models import OfferCategory, Offer, OfferPhoto, CloseReason
from cities.models import City#, Region

class CloseReasonSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = CloseReason


class OfferCategorySerializer(serializers.ModelSerializer):
    class Meta:
    
        fields = '__all__'
        model = OfferCategory

class OfferNotClosedSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)
    category = serializers.SlugRelatedField(slug_field='id', queryset = OfferCategory.objects.all())
    city = serializers.SlugRelatedField(slug_field='id', queryset = City.objects.all(), required=False)
    
    class Meta:
        fields = ("pk", "author", "title", "description", "category", "is_service",
     "is_used", "city", "pub_date", "is_private", "moderation_statuses", "is_closed", "photos")       
        model = Offer
        read_only_fields=("moderation_statuses",)
         
class OfferNotClosedSerializerModeration(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)
    category = serializers.SlugRelatedField(slug_field='id', queryset = OfferCategory.objects.all())
    city = serializers.SlugRelatedField(slug_field='id', queryset = City.objects.all(), required=False)
    
    class Meta:
        fields = ("pk", "author", "title", "description", "category", "is_service",
     "is_used", "city", "pub_date", "is_private", "moderation_statuses", "is_closed", "photos")       
        model = Offer

class OfferClosedSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)
    category = serializers.SlugRelatedField(slug_field='id', queryset = OfferCategory.objects.all())
    city = serializers.SlugRelatedField(slug_field='id', queryset = City.objects.all())
    close_reason = serializers.SlugRelatedField(slug_field='id', queryset = CloseReason.objects.all())
    
    class Meta:
        fields = '__all__'
        model = Offer


#class OfferNotClosedSerializer(serializers.ModelSerializer):
#    author = serializers.SlugRelatedField(slug_field='username', read_only=True)
#    category = serializers.SlugRelatedField(slug_field='id', queryset = OfferCategory.objects.all())
#    city = serializers.SlugRelatedField(slug_field='id', queryset = City.objects.all(), required=False)

    
#    class Meta:
#        fields = ("pk", "author", "title", "description", "category", "is_service",
#     "is_used", "city", "pub_date", "is_private", "moderation_statuses", "is_closed", "photos")       
#        model = Offer


class OfferPhotoSerializer(serializers.ModelSerializer):
    offer = serializers.SlugRelatedField(slug_field='id', read_only=True)

    class Meta:
        fields = '__all__'
        model = OfferPhoto


#class CitySerializer(serializers.ModelSerializer):
#    region = serializers.SlugRelatedField(slug_field='id', queryset = Region.objects.all())

#    class Meta:
#        fields = '__all__'
#        model = City

        
#class RegionSerializer(serializers.ModelSerializer):
#    class Meta:
#        fields = '__all__'
#        model = Region
