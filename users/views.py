from django.conf import settings
from django.contrib.auth import get_user_model
from phone_verify.serializers import PhoneSerializer, SMSVerificationSerializer
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import \
    TokenObtainPairView as BaseTokenObtainPairView
from rest_framework_simplejwt.views import \
    TokenRefreshView as BaseTokenRefreshView
from social_core import exceptions as social_exceptions
from social_core.backends.utils import load_backends as load_social_backends
from social_django import utils as social_utils

from . import responses, serializers, utils
from .models import SocialMedia

User = get_user_model()


class MeUserView(RetrieveUpdateAPIView):
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user


class PhoneVerificationViewSet(GenericViewSet):

    @action(detail=False, methods=["POST"], permission_classes=[AllowAny],
        serializer_class=PhoneSerializer)
    def register(self, request):
        serializer = PhoneSerializer(data=request.data)
        if not serializer.is_valid():
            return responses.INVALID_PHONE_NUMBER

        phone_number = str(serializer.validated_data['phone_number'])
        if User.phone_is_used(phone_number):
            return responses.USED_PHONE_NUMBER

        try:
            session_token = utils.send_security_code(phone_number)
            return responses.create_response(
                200000,
                {'session_token': session_token}
            )
        except Exception:
            return responses.SMS_SENDING_ERROR

    @action(detail=False, methods=["POST"], permission_classes=[AllowAny],
        serializer_class=SMSVerificationSerializer,)
    def verify(self, request):
        serializer = SMSVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return responses.INVALID_SECURITY_CODE
        return responses.VALID_SECURITY_CODE

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny],
            serializer_class=serializers.CreateUserSerializer)
    def signup(self, request):
        serializer = SMSVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return responses.INVALID_SECURITY_CODE

        serializer = serializers.CreateUserSerializer(data=request.data)
        if not serializer.is_valid():
            errors = ' '.join([
                ' '.join(msg) for msg in serializer.errors.values()
            ])
            return responses.invalid_registration_data(errors)

        try:
            serializer.save()
        except Exception:
            return responses.USER_CREATION_ERROR
        return responses.USER_CREATION_OK


class TokenObtainPairView(BaseTokenObtainPairView):
    serializer_class = serializers.TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except User.DoesNotExist:
            return responses.USER_NOT_FOUND
        except AuthenticationFailed:
            return responses.WRONG_PASSWORD
        except PermissionDenied:
            return responses.USER_IS_BLOCKED
        except Exception as err:
            return responses.TOKEN_GENERATION_ERROR

        return responses.create_response(200000, serializer.validated_data)


class TokenRefreshView(BaseTokenRefreshView):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return responses.INVALID_REFRESH_TOKEN
        except Exception:
            return responses.TOKEN_GENERATION_ERROR

        return responses.create_response(200000, serializer.validated_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_social_providers(request):
    backends = load_social_backends(settings.AUTHENTICATION_BACKENDS)
    providers = []
    strategy = social_utils.load_strategy(request)
    for backend_name, backend_class in backends.items():
        backend = backend_class(
            strategy=strategy,
            redirect_uri=settings.SOCIAL_AUTH_LOGIN_REDIRECT_URL
        )
        try:
            social_media = SocialMedia.objects.get(oauth_backend=backend_name)
            title = social_media.name
            logo = social_media.logo.url
        except SocialMedia.DoesNotExist:
            title = ''
            logo = ''

        providers.append({
            'name': backend_name,
            'title': title,
            'logo': logo,
            'auth_url': backend.auth_url()
        })
    return responses.create_response(200000, {'providers': providers})


@api_view(['POST'])
@permission_classes([AllowAny])
def convert_social_token(request):
    provider = request.data.get('provider', '')
    token = request.data.get('token', '')
    strategy = social_utils.load_strategy(request)
    try:
        backend = social_utils.load_backend(
            strategy=strategy,
            name=provider,
            redirect_uri=None
        )
    except social_exceptions.MissingBackend:
        return responses.INVALID_SOCIAL_PROVIDER

    user = backend.do_auth(token)
    if user is None:
        return responses.INVALID_OAUTH_TOKEN

    if not user.is_active:
        return responses.USER_IS_BLOCKED

    try:
        refresh = RefreshToken.for_user(user)
        return responses.create_response(200000, {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
    except Exception:
        return responses.TOKEN_GENERATION_ERROR
