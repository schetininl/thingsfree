import logging

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import \
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)
User = get_user_model()


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'phone_number', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'phone_number': {
                'required': True
            }
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    username_field = 'user'

    def validate(self, attrs):
        authenticate_kwargs = {
            'username': attrs['user'],
            'password': attrs['password'],
            'raise_exception': True
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        try:
            self.user = authenticate(**authenticate_kwargs)
        except Exception as err:
            logger.error(f'Error in user authentication: {err}')
            raise err

        refresh = self.get_token(self.user)
        return {
            'access': str(refresh.access_token),
            'expires_in': refresh.access_token.get('exp', ''),
            'refresh': str(refresh)
        }


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        data = {
            'access': str(refresh.access_token),
            'expires_in': refresh.access_token.get('exp', '')
        }

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()

            data['refresh'] = str(refresh)

        return data


class OAuthTokenSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=32)
    token = serializers.CharField(max_length=4096)
