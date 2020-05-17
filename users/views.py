from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from phone_verify.api import VerificationViewSet
from phone_verify.serializers import PhoneSerializer, SMSVerificationSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import CreateUserSerializer

User = get_user_model()


class PhoneVerificationViewSet(VerificationViewSet):

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny],
            serializer_class=PhoneSerializer)
    def register(self, request):
        phone_number = request.data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            return Response(
                {'message': _('A user with that phone already exists.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().register(request)

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny],
            serializer_class=CreateUserSerializer)
    def signup(self, request):
        serializer = SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)