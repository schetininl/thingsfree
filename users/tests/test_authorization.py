import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test.client import Client
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from social_core.backends.base import BaseAuth
from social_django.models import UserSocialAuth

User = get_user_model()


class TestTokenObtain:
    """Набор тестов для тестирования выдачи JWT-токенов."""

    url = '/api/v1/token/'

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('user_field', ['username', 'email', 'phone_number'])
    def test_successful_obtain(self, client, existent_user, default_password, user_field):
        msg_pattern = f'При POST запросе {self.url} с валидными данными {{}}'

        request_body = {
            'user': getattr(existent_user, user_field),
            'password': default_password
        }
        response = client.post(self.url, data=request_body)

        assert response.status_code == 200, \
            msg_pattern.format(pytest.http_status_not_200)

        response_data = response.json()

        assert response_data.get('status') == 200000, \
            msg_pattern.format('статус бизнес-логики не равен 200000')

        response_body = response_data.get('body')
        access_token = response_body.get('access', '')
        refresh_token = response_body.get('refresh', '')
        assert access_token != '', \
            msg_pattern.format('в теле ответа не содержится токен доступа')
        assert refresh_token != '', \
            msg_pattern.format('в теле ответа не содержится refresh-токен')

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('user_field', ['username', 'email', 'phone_number'])
    def test_nonexistent_user(self, client, nonexistent_user, default_password, user_field):
        msg_pattern = f'При POST запросе {self.url} с данными несуществующего' \
                      f' пльзователя {{}}'

        request_body = {
            'user': nonexistent_user[user_field],
            'password': default_password
        }
        response = client.post(self.url, data=request_body)
        assert response.status_code == 400, \
            msg_pattern.format(pytest.http_status_not_400)

        response_data = response.json()

        assert response_data.get('status') == 400005, \
            msg_pattern.format('статус бизнес-логики не равен 400005')

        response_body = response_data.get('body')
        actual_msg = response_body.get('message')
        assert actual_msg == _('User not found.'), \
            msg_pattern.format(pytest.wrong_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('user_field', ['username', 'email', 'phone_number'])
    def test_wrong_password(self, client, existent_user, default_password, user_field):
        msg_pattern = f'При POST запросе {self.url} с неверным паролем {{}}'

        request_body = {
            'user': getattr(existent_user, user_field),
            'password': default_password + '1'
        }
        response = client.post(self.url, data=request_body)

        assert response.status_code == 400, \
            msg_pattern.format(pytest.http_status_not_400)

        response_data = response.json()

        assert response_data.get('status') == 400006, \
            msg_pattern.format('статус бизнес-логики не равен 400006')

        response_body = response_data.get('body')
        actual_msg = response_body.get('message')
        assert actual_msg == _('Wrong password.'), \
            msg_pattern.format(pytest.wrong_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('user_field', ['username', 'email', 'phone_number'])
    def test_blocked_user(self, client, blocked_user, default_password, user_field):
        msg_pattern = f'При POST запросе {self.url} с данными ' \
                      f'заблокированного пользователя {{}}'

        request_body = {
            'user': getattr(blocked_user, user_field),
            'password': default_password
        }
        response = client.post(self.url, data=request_body)

        assert response.status_code == 400, \
            msg_pattern.format(pytest.http_status_not_400)

        response_data = response.json()

        assert response_data.get('status') == 400007, \
            msg_pattern.format('статус бизнес-логики не равен 400007')

        response_body = response_data.get('body')
        actual_msg = response_body.get('message')
        assert actual_msg == _('The user is blocked.'), \
            msg_pattern.format(pytest.wrong_msg)


class TestTokenRefresh:
    """Набор тестов для тестирования обновления токена доступа."""

    url = '/api/v1/token/refresh/'

    @pytest.mark.django_db(transaction=True)
    def test_successful_refresh(self, client, refresh_token):
        msg_pattern = f'При POST запросе {self.url} с валидными данными {{}}'

        request_body = {
            'refresh': refresh_token
        }
        response = client.post(self.url, data=request_body)

        assert response.status_code == 200, \
            msg_pattern.format(pytest.http_status_not_200)

        response_data = response.json()

        assert response_data.get('status') == 200000, \
            msg_pattern.format('статус бизнес-логики не равен 200000')

        response_body = response_data.get('body')
        access_token = response_body.get('access', '')
        assert access_token != '', \
            msg_pattern.format('в теле ответа не содержится токен доступа')

    @pytest.mark.django_db(transaction=True)
    def test_invalid_refres_token(self, client, invalid_refresh_token):
        msg_pattern = f'При POST запросе {self.url} с невалидными данными {{}}'

        request_body = {
            'refresh': invalid_refresh_token
        }
        response = client.post(self.url, data=request_body)

        assert response.status_code == 400, \
            msg_pattern.format(pytest.http_status_not_400)

        response_data = response.json()

        assert response_data.get('status') == 400008, \
            msg_pattern.format('статус бизнес-логики не равен 400008')

        response_body = response_data.get('body')
        actual_msg = response_body.get('message')
        assert actual_msg == _('Invalid refresh-token.'), \
            msg_pattern.format(pytest.wrong_msg)


@pytest.mark.django_db(transaction=True)
class TestConvertSocialToken:
    """Набор тестов для авторизации через социальные сети."""

    url = '/api/v1/social/convert_token/'
    client = Client()
    providers = ['vk-oauth2', 'odnoklassniki-oauth2', 'facebook']

    def post(self, request_body):
        response = self.client.post(self.url, data=request_body)
        response_data = response.json()
        response_body = response_data.get('body', {})
        app_status = response_data.get('status', 0)

        return response.status_code, app_status, response_body

    @pytest.mark.parametrize('provider', providers)
    def test_successful_conversion(self, provider, valid_oauth_token,
                                     social_user_data, mock_get_user_data,
                                     monkeypatch):
        msg_pattern = f'При POST запросе {self.url} с валидными данными {{}}'
        monkeypatch.setattr(BaseAuth, 'get_json', mock_get_user_data)
        http_status, app_status, response_body = self.post({
            'provider': provider,
            'token': valid_oauth_token
        })

        assert http_status == 200, msg_pattern.format(
            pytest.http_status_not_200)
        assert app_status == 200000, msg_pattern.format(
            pytest.app_status_not_200000)

        assert 'access' in response_body, msg_pattern.format(
            'в теле ответа не содержится токен доступа')
        assert 'expires_in' in response_body, msg_pattern.format(
            'в теле ответа не содержится время жизни токена')
        assert 'refresh' in response_body, msg_pattern.format(
            'в теле ответа не содежится refresh-токен')

        try:
            token = AccessToken(response_body['access'])
            user = User.objects.get(id=token['user_id'])
        except Exception:
            user = None

        assert user is not None, msg_pattern.format(
            'в теле ответа содержится невалидный токен')

        user_data = social_user_data[provider]
        assert user_data['first_name'] == user.first_name, msg_pattern.format(
            'у созданного пользователя неверно заполнено имя')
        assert user_data['last_name'] == user.last_name, msg_pattern.format(
            'у созданного пользователя неверно заполнена фамилия')

        if 'email' in user_data:
            assert user_data['email'] == user.email, msg_pattern.format(
                'у созданного пользователя неверно заполнен email')

    @pytest.mark.parametrize('provider', providers)
    def test_invalid_token(self, provider, invalid_oauth_token,
                           mock_get_user_data, monkeypatch):
        msg_pattern = f'При POST запросе {self.url} с невалидным токеном {{}}'
        monkeypatch.setattr(BaseAuth, 'get_json', mock_get_user_data)
        http_status, app_status, response_body = self.post({
            'provider': provider,
            'token': invalid_oauth_token
        })

        assert http_status == 400, msg_pattern.format(
            pytest.http_status_not_400)
        assert app_status == 400010, msg_pattern.format(
            'статус бизнес-логики не равен 400010')

        assert response_body.get('message', '') == _('Invalid token.'), \
            msg_pattern.format(pytest.wrong_message)

    def test_invalid_provider(self, valid_oauth_token):
        msg_pattern = f'При POST запросе {self.url} ' \
                      f'с несуществующим провайдером {{}}'
        http_status, app_status, response_body = self.post({
            'provider': 'unknown_provider',
            'token': valid_oauth_token
        })

        assert http_status == 400, msg_pattern.format(
            pytest.http_status_not_400)
        assert app_status == 400009, msg_pattern.format(
            'статус бизнес-логики не равен 400009')

        assert response_body.get('message', '') == _('Provider is not found.'),\
            msg_pattern.format(pytest.wrong_message)

    def test_blocked_user(self, vk_provider, social_user_data,
                          valid_oauth_token, mock_get_user_data, monkeypatch):
        msg_pattern = f'При POST запросе {self.url} с токеном ' \
                      f'заблокированного пользователя {{}}'
        monkeypatch.setattr(BaseAuth, 'get_json', mock_get_user_data)

        user_data = social_user_data[vk_provider]
        user = User.objects.create_user(
            username=user_data['screen_name'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_active=False
        )
        social_user = UserSocialAuth.objects.create(
            user=user,
            provider=vk_provider,
            uid=user_data['id']
        )

        http_status, app_status, response_body = self.post({
            'provider': vk_provider,
            'token': valid_oauth_token
        })

        assert http_status == 400, msg_pattern.format(
            pytest.http_status_not_400)
        assert app_status == 400007, msg_pattern.format(
            'статус бизнес-логики не равен 400007')

        assert response_body.get('message', '') == _('The user is blocked.'),\
            msg_pattern.format(pytest.wrong_message)

        assert User.objects.all().count() == 1, msg_pattern.format(
            'создан дубль пользователя')
        assert UserSocialAuth.objects.all().count() == 1, msg_pattern.format(
            'создан дубль пользователя')

    def test_token_generation_error(self, random_social_provider,
                                    valid_oauth_token, mock_get_user_data,
                                    monkeypatch):
        msg_pattern = f'При POST запросе {self.url}, приводящем к ошибке ' \
                      f'генерации токена {{}}'
        monkeypatch.setattr(BaseAuth, 'get_json', mock_get_user_data)

        def mock_generate_token(cls, user):
            raise Exception

        monkeypatch.setattr(RefreshToken, 'for_user', mock_generate_token)

        http_status, app_status, response_body = self.post({
            'provider': random_social_provider,
            'token': valid_oauth_token
        })

        assert http_status == 500, msg_pattern.format(
            pytest.http_status_not_500)
        assert app_status == 500003, msg_pattern.format(
            'статус бизнес-логики не равен 500003')

        assert response_body.get('message', '') == _('Error in token generation.'),\
            msg_pattern.format(pytest.wrong_message)

    def test_user_creation_error(self, vk_provider, valid_oauth_token,
                                 social_user_data, mock_get_user_data, monkeypatch):
        msg_pattern = f'При POST запросе {self.url}, приводящем к ошибке ' \
                      f'создания пользователя {{}}'
        monkeypatch.setattr(BaseAuth, 'get_json', mock_get_user_data)

        def mock_user_save(*args, **kwargs):
            raise IntegrityError
        monkeypatch.setattr(User, 'save', mock_user_save)

        http_status, app_status, response_body = self.post({
            'provider': vk_provider,
            'token': valid_oauth_token
        })

        assert http_status == 500, msg_pattern.format(
            pytest.http_status_not_500)
        assert app_status == 500002, msg_pattern.format(
            'статус бизнес-логики не равен 500002')
