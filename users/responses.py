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

INVALID_PHONE_NUMBER = message(400001, _('Phone number is not valid.'))
USED_PHONE_NUMBER = message(400002, _('A user with that phone already exists.'))
INVALID_SECURITY_CODE = message(400003, _('Security code is not valid.'))

SMS_SENDING_ERROR = message(500001, _('Error in sending verification code.'))
USER_CREATION_ERROR = message(500002, _('User account has not been created.'))


def invalid_registration_data(errors):
    return message(400004, errors)
