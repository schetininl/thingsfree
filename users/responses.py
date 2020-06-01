from django.utils.translation import gettext_lazy as _
from rest_framework import status as http_statuses
from rest_framework.response import Response


class BaseResponse(Response):
    def __init__(self, http_status, application_status, body):
        super().__init__(
            data={
                'status': application_status,
                'body': body
            },
            status=http_status
        )


class InvalidPhoneNumber(BaseResponse):
    def __init__(self):
        super().__init__(
            http_status=http_statuses.HTTP_400_BAD_REQUEST,
            application_status=400001,
            body={
                'message': _('Phone number is not correct.')
            }
        )


class PhoneNumberIsUsed(BaseResponse):
    def __init__(self):
        super().__init__(
            http_status=http_statuses.HTTP_400_BAD_REQUEST,
            application_status=400002,
            body={
                'message': _('A user with that phone already exists.')
            }
        )


class SMSSendingFailed(BaseResponse):
    def __init__(self):
        super().__init__(
            http_status=http_statuses.HTTP_500_INTERNAL_SERVER_ERROR,
            application_status=500001,
            body={
                'message': _('Error in sending verification code.')
            }
        )


class ValidSecurityCode(BaseResponse):
    def __init__(self):
        def __init__(self):
            super().__init__(
                http_status=http_statuses.HTTP_200_OK,
                application_status=200000,
                body={
                    'message': _('Security code is valid.')
                }
            )


class InvalidSecurityCode(BaseResponse):
    def __init__(self):
        super().__init__(
            http_status=http_statuses.HTTP_400_BAD_REQUEST,
            application_status=400003,
            body={
                'message': _('Security code is not valid.')
            }
        )
