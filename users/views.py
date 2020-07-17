from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.utils import DatabaseError
from phone_verify.serializers import PhoneSerializer, SMSVerificationSerializer
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import \
    AuthenticationFailed, PermissionDenied, NotAuthenticated
from rest_framework.pagination import LimitOffsetPagination
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
from .models import SocialMedia, Following

User = get_user_model()


class PhoneVerificationViewSet(GenericViewSet):

    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
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

    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def verify(self, request):
        serializer = SMSVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return responses.INVALID_SECURITY_CODE
        return responses.VALID_SECURITY_CODE

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
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

    @action(detail=False, methods=['POST'])
    def bind(self, request):
        serializer = SMSVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return responses.INVALID_SECURITY_CODE

        user = request.user
        user.phone_number = serializer.validated_data.get('phone_number', '')
        try:
            user.save()
        except Exception:
            return responses.USER_UPDATE_ERROR
        return responses.USER_UPDATE_OK


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
        except Exception:
            return responses.TOKEN_GENERATION_ERROR

        return responses.create_response(200000, serializer.validated_data)


class TokenRefreshView(BaseTokenRefreshView):
    serializer_class = serializers.TokenRefreshSerializer

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
    serializer = serializers.OAuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    provider = serializer.validated_data['provider']
    token = serializer.validated_data['token']
    strategy = social_utils.load_strategy(request)
    try:
        backend = social_utils.load_backend(
            strategy=strategy,
            name=provider,
            redirect_uri=None
        )
    except social_exceptions.MissingBackend:
        return responses.INVALID_SOCIAL_PROVIDER

    user = None

    try:
        user = backend.do_auth(token)
    except DatabaseError:
        return responses.USER_CREATION_ERROR
    except Exception:
        return responses.INVALID_OAUTH_TOKEN

    if not user.is_active:
        return responses.USER_IS_BLOCKED

    try:
        refresh = RefreshToken.for_user(user)
        return responses.create_response(200000, {
            'access': str(refresh.access_token),
            'expires_in': refresh.access_token.get('exp', ''),
            'refresh': str(refresh)
        })
    except Exception:
        return responses.TOKEN_GENERATION_ERROR


class FollowingViewSet(GenericViewSet):
    pagination_class = LimitOffsetPagination

    def get_user(self, request, user_id):
        if user_id == 'me':
            is_authenticated = bool(request.user and request.user.is_authenticated)
            if not is_authenticated:
                raise NotAuthenticated
            return request.user

        return get_object_or_404(User, pk=user_id)

    def get_follow_list_response(self, request, target_user_id):
        """
        Возвращает объект `Response` со списком подписчиков или
        подписок (в зависимости от вызванного метода) пользователя с
        идентификатором target_user_id.
        """
        assert self.action in ('followers', 'following')
        target_user = self.get_user(request, target_user_id)
        if self.action == 'followers':
            queryset = target_user.followers.all()
            lookup_field = 'follower'
        else:
            queryset = target_user.following.all()
            lookup_field = 'author'

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ShortUserProfileSerializer(
                [getattr(obj, lookup_field) for obj in page],
                many=True
            )
            paginated_response = super().get_paginated_response(serializer.data)
            return responses.create_response(
                200000,
                paginated_response.data
            )

        serializer = serializers.ShortUserProfileSerializer(
            [getattr(obj, lookup_field) for obj in queryset],
            many=True
        )
        return responses.create_response(200000, serializer.data)

    @action(detail=False, methods=['GET'], permission_classes=[AllowAny],
            name='followers')
    def followers(self, request, user_id):
        return self.get_follow_list_response(request, user_id)

    @action(detail=False, methods=['GET'], permission_classes=[AllowAny],
            name='following')
    def following(self, request, user_id):
        return self.get_follow_list_response(request, user_id)

    @action(detail=False, methods=['POST'], name='follow')
    def follow(self, request, user_id):
        author = self.get_user(request, user_id)
        if author == request.user:
            return responses.FOLLOWING_MYSELF

        if not author.is_active:
            return responses.USER_IS_BLOCKED

        try:
            following, created = Following.objects.get_or_create(
                author=author,
                follower=request.user
            )
            if not created:
                return responses.FOLLOWING_EXISTS
        except:
            return responses.FOLLOWING_CREATION_ERROR

        return responses.FOLLOWING_CREATION_OK

    @action(detail=False, methods=['POST'], name='unfollow')
    def unfollow(self, request, user_id):
        author = self.get_user(request, user_id)
        deleted, _ = (
            Following.objects
            .filter(author=author, follower=request.user)
            .delete()
        )
        if not deleted:
            return responses.FOLLOWING_DOES_NOT_EXISTS
        return responses.FOLLOWING_REMOVED
