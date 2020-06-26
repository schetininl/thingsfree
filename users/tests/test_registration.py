from unittest import mock

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.utils.translation import gettext_lazy as _
from phone_verify.models import SMSVerification

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestSecurityCodeSending:
    """Набор тестов для отправки СМС с кодом подтверждения."""

    url = '/api/v1/phone/register/'
    client = Client()

    def post(self, request_body):
        response = self.client.post(self.url, data=request_body)
        response_data = response.json()
        response_body = response_data.get('body', {})
        app_status = response_data.get('status', 0)

        return response.status_code, app_status, response_body

    @pytest.fixture(autouse=True)
    def methods_for_mock(self, sms_send_method):
        self.sms_send_method = sms_send_method

    def test_successful_sending(self, valid_phone_number):
        msg_pattern = f'При POST запросе {self.url} с валидными данными {{}}'

        with mock.patch(self.sms_send_method) as sender_mock:
            http_status, app_status, response_body = self.post({
                'phone_number': valid_phone_number
            })
            assert http_status == 200, msg_pattern.format(
                pytest.http_status_not_200)
            assert app_status == 200000, msg_pattern.format(
                pytest.app_status_not_200000)

            queryset = SMSVerification.objects.filter(
                phone_number=valid_phone_number
            )
            assert queryset.exists(), msg_pattern.format(
                'не был сгенерирован код подтверждения')

            verification = queryset.first()
            actual_session_token = response_body.get('session_token')
            assert actual_session_token == verification.session_token, \
                msg_pattern.format('ответ содержит неверный токен сессии')

            assert sender_mock.called, msg_pattern.format(
                'не происходит отправка СМС сообщения')

            actual_number, sent_message = sender_mock.call_args.args
            assert actual_number == valid_phone_number, msg_pattern.format(
                'СМС отправлено на неверный номер')
            assert verification.security_code in sent_message, \
                msg_pattern.format('СМС не содержит код подтверждения')

    def test_invalid_phone_number(self, invalid_phone_number):
        msg_pattern = f'При POST запросе {self.url} с невалидными данными {{}}'

        with mock.patch(self.sms_send_method) as sender_mock:
            http_status, app_status, response_body = self.post({
                'phone_number': invalid_phone_number
            })
            assert http_status == 400, msg_pattern.format(
                pytest.http_status_not_400)
            assert app_status == 400001, msg_pattern.format(
                'статус бизнес-логики не равен 400001')

            assert not sender_mock.called, msg_pattern.format(
                'отправляется СМС')

            actual_msg = response_body.get('message')
            assert actual_msg == _('Phone number is not valid.'), \
                msg_pattern.format(pytest.wrong_msg)

    def test_used_phone_number(self, existent_user):
        msg_pattern = f'При POST запросе {self.url} телефоном, который ' \
                      f'уже используется другим пользователем {{}}'

        with mock.patch(self.sms_send_method) as sender_mock:
            http_status, app_status, response_body = self.post({
                'phone_number': existent_user.phone_number
            })
            assert http_status == 400, msg_pattern.format(
                pytest.http_status_not_400)
            assert app_status == 400002, msg_pattern.format(
                'статус бизнес-логики не равен 400002')

            assert not sender_mock.called, msg_pattern.format(
                'отправляется СМС')

            actual_msg = response_body.get('message')
            assert actual_msg == _('A user with that phone already exists.'), \
                msg_pattern.format(pytest.wrong_msg)

    def test_sms_sending_error(self, sms_sending_exception, valid_phone_number):
        msg_pattern = f'При POST запросе {self.url} с неработающим бэкэндом ' \
                      f'отправки СМС {{}}'

        with mock.patch(self.sms_send_method, side_effect=sms_sending_exception):
            http_status, app_status, response_body = self.post({
                'phone_number': valid_phone_number
            })
            assert http_status == 500, msg_pattern.format(
                pytest.http_status_not_500)
            assert app_status == 500001, msg_pattern.format(
                'статус бизнес-логики не равен 500001')

            actual_msg = response_body.get('message')
            assert actual_msg == _('Error in sending verification code.'), \
                msg_pattern.format(pytest.wrong_msg)


@pytest.mark.django_db(transaction=True)
class TestSecurityCodeVerification:
    """Набор тестов для проверки кода подтверждения из СМС."""

    url = '/api/v1/phone/verify/'
    client = Client()

    def post(self, request_body):
        response = self.client.post(self.url, data=request_body)
        response_data = response.json()
        response_body = response_data.get('body', {})
        app_status = response_data.get('status', 0)

        return response.status_code, app_status, response_body

    def test_valid_security_code(self, valid_verification_data):
        msg_pattern = f'При POST запросе {self.url} с верным кодом ' \
                      f'подтверждения {{}}'
        http_status, app_status, response_body = self.post(valid_verification_data)
        assert http_status == 200, msg_pattern.format(
            pytest.http_status_not_200)
        assert app_status == 200000, msg_pattern.format(
            pytest.app_status_not_200000)
        assert response_body.get('message') == _('Security code is valid.'), \
            msg_pattern.format(pytest.wrong_msg)

    def test_invalid_verification_data(self, client, invalid_verification_data):
        msg_pattern = f'При POST запросе {self.url} с неверным кодом ' \
                      f'подтверждения {{}}'
        http_status, app_status, response_body = self.post(
            invalid_verification_data)
        assert http_status == 400, msg_pattern.format(
            pytest.http_status_not_400)
        assert app_status == 400003, msg_pattern.format(
            'статус бизнес-логики не равен 400003')
        assert response_body.get('message') == _('Security code is not valid.'), \
            msg_pattern.format(pytest.wrong_msg)


@pytest.mark.django_db(transaction=True)
class TestSignup:
    """Набор тестов для регистрации нового аккаунта."""
    
    url = '/api/v1/phone/signup/'
    client = Client()

    def post(self, request_body):
        response = self.client.post(self.url, data=request_body)
        response_data = response.json()
        response_body = response_data.get('body', {})
        app_status = response_data.get('status', 0)

        return response.status_code, app_status, response_body

    def test_successful_signup(self, valid_signup_data):
        msg_pattern = f'При POST запросе {self.url} с корректными данными {{}}'
        http_status, app_status, response_body = self.post(valid_signup_data)

        assert http_status == 201, msg_pattern.format(
            pytest.http_status_not_201)
        assert app_status == 201000, msg_pattern.format(
            pytest.app_status_not_201000)

        assert response_body.get('message') == _('User account has been created.'), \
            msg_pattern.format(pytest.wrong_msg)

        try:
            new_user = User.objects.get(username=valid_signup_data['username'])
        except User.DoesNotExist:
            new_user = None

        assert new_user is not None, msg_pattern.format(
            'в базе данных не создан пользователь')

    def test_invalid_verification_data(self, signup_data_invalid_verification):
        msg_pattern = f'При POST запросе {self.url} с неверным кодом ' \
                      f'подтверждения {{}}'
        http_status, app_status, response_body = self.post(
            signup_data_invalid_verification)

        assert http_status == 400, msg_pattern.format(
            pytest.http_status_not_400)
        assert app_status == 400003, msg_pattern.format(
            'статус бизнес-логики не равен 400003')

        assert response_body.get('message') == _('Security code is not valid.'), \
            msg_pattern.format(pytest.wrong_msg)

        assert not User.objects.all().exists(), msg_pattern.format(
            'в базе данных создан пользователь')

    def test_invalid_registration_data(self, signup_data_invalid_username):
        msg_pattern = f'При POST запросе {self.url} с некорректным username {{}}'
        count_of_users_before = User.objects.all().count()
        http_status, app_status, response_body = self.post(
            signup_data_invalid_username)

        assert http_status == 400, msg_pattern.format(
            pytest.http_status_not_400)
        assert app_status == 400004, msg_pattern.format(
            'статус бизнес-логики не равен 400004')

        assert User.objects.all().count() == count_of_users_before, \
            msg_pattern.format('в базе данных создан пользователь')

    def test_server_error(self, valid_signup_data, mock_user_save, monkeypatch):
        msg_pattern = f'При POST запросе {self.url}, приводящем к внутренней ' \
                      f'ошибке сервера {{}}'
        monkeypatch.setattr(User, 'save', mock_user_save)
        http_status, app_status, response_body = self.post(valid_signup_data)

        assert http_status == 500, msg_pattern.format(
            pytest.http_status_not_500)
        assert app_status == 500002, msg_pattern.format(
            'статус бизнес-логики не равен 500002')

        assert response_body.get('message') == _('User account has not been created.'), \
            msg_pattern.format(pytest.wrong_msg)


@pytest.mark.django_db(transaction=True)
class TestBindPhoneNumber:
    """Набор тестов для привязки номера телефона к аккаунту."""

    url = '/api/v1/phone/bind/'

    def post(self, client, request_body):
        response = client.post(self.url, data=request_body)
        response_data = response.json()
        response_body = response_data.get('body', {})
        app_status = response_data.get('status', 0)

        return response.status_code, app_status, response_body

    def test_successful_bind(self, user_client, existent_user,
                             valid_verification_data):
        msg_pattern = f'При POST запросе {self.url} с валидными данными {{}}'
        http_status, app_status, response_body = self.post(
            user_client, valid_verification_data)

        assert http_status == 200, msg_pattern.format(
            pytest.http_status_not_200)
        assert app_status == 200000, msg_pattern.format(
            pytest.app_status_not_200000)

        existent_user.refresh_from_db()
        current_phone = str(existent_user.phone_number)
        assert current_phone == valid_verification_data['phone_number'], \
            msg_pattern.format('телефонный номер пользователя не был изменен')

    def test_unauthorized_user(self, client, valid_verification_data):
        msg_pattern = f'При POST запросе {self.url} без токена доступа {{}}'
        http_status, app_status, response_body = self.post(
            client, valid_verification_data)

        assert http_status == 401, msg_pattern.format(
            pytest.http_status_not_401)
        assert app_status == 401000, msg_pattern.format(
            'статус бизнес-логики не равен 401000')

    def test_invalid_security_code(self, user_client, invalid_verification_data):
        msg_pattern = f'При POST запросе {self.url} с неверным ' \
                      f'кодом подтверждения {{}}'
        http_status, app_status, response_body = self.post(
            user_client, invalid_verification_data)

        assert http_status == 400, msg_pattern.format(
            pytest.http_status_not_400)
        assert app_status == 400003, msg_pattern.format(
            'статус бизнес-логики не равен 400003')

    def test_server_error(self, user_client, valid_verification_data,
                          mock_user_save, monkeypatch):
        msg_pattern = f'При POST запросе {self.url} с валидными данными {{}}'
        monkeypatch.setattr(User, 'save', mock_user_save)

        http_status, app_status, response_body = self.post(
            user_client, valid_verification_data)

        assert http_status == 500, msg_pattern.format(
            pytest.http_status_not_500)
        assert app_status == 500004, msg_pattern.format(
            'статус бизнес-логики не равен 500004')


@pytest.mark.usefixtures('social_providers_setup')
@pytest.mark.django_db(transaction=True)
class TestSocialProviders:
    """Набор тестов для выборки социальных сетей, доступных для авторизации."""

    url = '/api/v1/social/providers/'
    client = Client()

    def test_list_of_providers(self, social_providers):
        msg_pattern = f'При GET запросе {self.url} {{}}'
        response = self.client.get(self.url)

        assert response.status_code == 200, msg_pattern.format(
            pytest.http_status_not_200)

        response_data = response.json()
        assert response_data.get('status', 0) == 200000, msg_pattern.format(
            pytest.app_status_not_200000)

        response_body = response_data.get('body', {})
        assert 'providers' in response_body, msg_pattern.format(
            'тело ответа не содержит список провайдеров')

        recieved_providers = response_body.get('providers', [])
        assert len(recieved_providers) == len(social_providers), \
            msg_pattern.format('ответ содержит неверное количество провайдеров')

        recieved_providers.sort(key=lambda x: x['name'])
        social_providers.sort(key=lambda x: x['name'])

        for i in range(len(social_providers)):
            assert recieved_providers[i]['name'] == social_providers[i]['name'], \
                msg_pattern.format('ответ содержит неверные данные')
            assert recieved_providers[i]['title'] == social_providers[i]['title'], \
                msg_pattern.format('ответ содержит неверные данные')

            expected_url = social_providers[i]['url']
            actual_url = recieved_providers[i]['auth_url']
            assert actual_url.startswith(expected_url), \
                msg_pattern.format('ответ содержит неверные url')

            setting_key = 'SOCIAL_AUTH_{}_KEY'.format(
                social_providers[i]['name'].replace('-', '_').upper())
            assert getattr(settings, setting_key) in actual_url, \
                msg_pattern.format('ответ содержит неверные url')

            assert 'logo' in recieved_providers[i], msg_pattern.format(
                'ответ не содержит логотипов социальных сетей')
