from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import \
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer

from .models import OAuthApplication

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
            raise err

        refresh = self.get_token(self.user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class SocialProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = OAuthApplication
        fields = ('name', 'client_id', 'logo')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        backend = instance.get_backend()
        auth_params = backend.auth_extra_arguments()
        ret['auth_url'] = backend.auth_url()
        ret['response_type'] = auth_params.get('response_type', backend.RESPONSE_TYPE)
        return ret
