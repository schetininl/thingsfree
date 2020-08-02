from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response


def create_response(status, body):
    # статус http ответа совпадает с первыми тремя цифрами статуса бизнес-логики
    http_status = status // 1000
    return Response(
        data={
            'status': status,
            'body': body
        },
        status=http_status
    )


def message(status, text):
    return create_response(status, {'message': text})


VALID_SECURITY_CODE = message(200000, _('Security code is valid.'))
USER_CREATION_OK = message(201000, _('User account has been created.'))
USER_UPDATE_OK = message(200000, _('User account has been updated.'))
FOLLOWING_CREATION_OK = message(200000, _('The user has been followed.'))
FOLLOWING_REMOVED = message(200000, _('The user has been unfollowed.'))

INVALID_PHONE_NUMBER = message(400001, _('Phone number is not valid.'))
USED_PHONE_NUMBER = message(400002, _('A user with that phone already exists.'))
INVALID_SECURITY_CODE = message(400003, _('Security code is not valid.'))
USER_NOT_FOUND = message(400005, _('User not found.'))
WRONG_PASSWORD = message(400006, _('Wrong password.'))
USER_IS_BLOCKED = message(400007, _('The user is blocked.'))
INVALID_REFRESH_TOKEN = message(400008, _('Invalid refresh-token.'))
INVALID_SOCIAL_PROVIDER = message(400009, _('Provider is not found.'))
INVALID_OAUTH_TOKEN = message(400010, _('Invalid token.'))
FOLLOWING_EXISTS = message(400011, _('Subscription already exists.'))
FOLLOWING_DOES_NOT_EXISTS = message(400012, _('Subscription does not exist.'))
FOLLOWING_MYSELF = message(400013, _('Following myself is not allowed.'))

SMS_SENDING_ERROR = message(500001, _('Error in sending verification code.'))
USER_CREATION_ERROR = message(500002, _('User account has not been created.'))
TOKEN_GENERATION_ERROR = message(500003, _('Error in token generation.'))
USER_UPDATE_ERROR = message(500004, _('User account has not been updated.'))
FOLLOWING_CREATION_ERROR = message(500005, _('Error in follow creation.'))

def invalid_registration_data(errors):
    return message(400004, errors)
