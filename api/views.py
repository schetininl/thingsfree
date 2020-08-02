import logging

from django.core.exceptions import PermissionDenied
from django.http.response import Http404
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import set_rollback

logger = logging.getLogger(__name__)


def exception_handler(exc, context):

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            data = {'message': exc.detail}

        set_rollback()
        return Response(
            {
                'status': exc.status_code * 1000,
                'body': data
            },
            status=exc.status_code,
            headers=headers
        )

    view = context.get('view')
    logger.error(
        f'Exception in view {view}: '
        f'{exc}'
    )

    return Response(
        {
            'status': 500000,
            'body': {'message': 'Unknown error.'}
        },
        status=500
    )
