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


class OfferClosedSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)
    category = serializers.SlugRelatedField(slug_field='id', queryset = OfferCategory.objects.all())
    city = serializers.SlugRelatedField(slug_field='id', queryset = City.objects.all())
    close_reason = serializers.SlugRelatedField(slug_field='id', queryset = CloseReason.objects.all())
    
    class Meta:
        fields = '__all__'
        model = Offer


class OfferNotClosedSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)
    category = serializers.SlugRelatedField(slug_field='id', queryset = OfferCategory.objects.all())
    city = serializers.SlugRelatedField(slug_field='id', queryset = City.objects.all(), required=False)
    response = serializers.SerializerMethodField()
    user_menu_links=serializers.SerializerMethodField()

    def get_response(self, obj):
        return '200000'

    def get_user_menu_links(self, obj): 
        links= {
        "link_new_offer": "/offers/",
      
        "link_my_offers": "/offers/{id}",
    
        "link_my_likes": "To Be Determinted",
      
        "link_following": "users/me/following",
      
        "link_messages": "To Be Determinted"
        }     
        return(links)
        
    
    class Meta:
        fields = ("pk", "author", "title", "description", "category", "is_service",
     "is_used", "city", "pub_date", "is_private", "moderation_statuses", "is_closed", "photos", "response", "user_menu_links")       
        model = Offer


class OfferNotClosedHigherLevelSerializer(serializers.ModelSerializer):
    offers = OfferNotClosedSerializer(many=True)

    class Meta:
        fields = ("offers", )
        model = Offer


        

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
