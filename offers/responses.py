from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response


def create_response(status, body):
    # статус http ответа совпадает с первыми тремя цифрами статуса бизнес-логики
    http_status = status // 1000
    return Response(
        data={
            'status': status,
            'body': body,
            'user_menu_links': {
                "link_new_offer": "http://www.thingsfree/offers/",
      
                "link_my_offers": "http://www.thingsfree/offers/{id}",
    
                "link_my_likes": "To Be Determinted",
      
                "link_following": "users/me/following",
      
                "link_messages": "To Be Determinted"},
            'manage_profile': {
                "edit_profile_link": "http://www.thingsfree/users/me/",  
                "logout_profile_link": "To Be Determinted"
        }},
        status=http_status
    )


def message(status, text):
    return create_response(status, {'message': text})


OFFER_CREATION_OK = message(201100, _('Offer has been created.'))

INVALID_OFFER_TITLE = message(400101, _('Please fill the title.'))
INVALID_OFFER_DESCRIPTION = message(400102, _('Please fill the description.'))
INVALID_OFFER_CATEGORY = message(400103, _('Please fill the category.'))
OFFER_SAVING_ERROR = message(500101, _('Error in saving new offer.'))
