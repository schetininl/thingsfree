from unittest import mock

import pytest
from django.utils.translation import gettext_lazy as _
from phone_verify.models import SMSVerification


class TestSecurityCodeSending:

    url = '/api/v1/phone/register/'

    @pytest.fixture(autouse=True)
    def methods_for_mock(self, sms_send_method):
        self.sms_send_method = sms_send_method

    @pytest.mark.django_db(transaction=True)
    def test_successful_sending(self, client, valid_phone_number):

        msg_pattern = f'При POST запросе {self.url} с валидными данными {{}}'

        with mock.patch(self.sms_send_method) as sender_mock:
            request_body = {
                'phone_number': valid_phone_number
            }
            response = client.post(self.url, data=request_body)

            assert response.status_code == 200, \
                msg_pattern.format('HTTP статус ответа не равен 200')

            response_data = response.json()

            assert response_data.get('status') == 200000, \
                msg_pattern.format('статус бизнес-логики не равен 200000')

            response_body = response_data.get('body')
            queryset = SMSVerification.objects.filter(
                phone_number=valid_phone_number
            )

            assert queryset.exists(), \
                msg_pattern.format('не был сгенерирован код подтверждения')

            verification = queryset.first()
            actual_session_token = response_body.get('session_token')

            assert actual_session_token == verification.session_token, \
                msg_pattern.format('ответ содержит неверный токен сессии')

            assert sender_mock.called, \
                msg_pattern.format('не происходит отправка СМС сообщения')

            actual_number, sent_message = sender_mock.call_args.args

            assert actual_number == valid_phone_number, \
                msg_pattern.format('СМС отправлено на неверный номер')

            assert verification.security_code in sent_message, \
                msg_pattern.format('СМС не содержит код подтверждения')

    @pytest.mark.django_db(transaction=True)
    def test_invalid_phone_number(self, client, invalid_phone_number):

        msg_pattern = f'При POST запросе {self.url} с невалидными данными {{}}'

        with mock.patch(self.sms_send_method) as sender_mock:
            request_body = {
                'phone_number': invalid_phone_number
            }
            response = client.post(self.url, data=request_body)

            assert response.status_code == 400, \
                msg_pattern.format('HTTP статус ответа не равен 400')

            response_data = response.json()

            assert response_data.get('status') == 400001, \
                msg_pattern.format('статус бизнес-логики не равен 400001')

            assert not sender_mock.called, \
                msg_pattern.format('отправляется СМС')

            response_body = response_data.get('body')
            actual_msg = response_body.get('message')
            assert actual_msg == _('Phone number is not valid.'), \
                msg_pattern.format('ответ содержит неверное сообщение')

    @pytest.mark.django_db(transaction=True)
    def test_used_phone_number(self, client, existent_user):

        msg_pattern = f'При POST запросе {self.url} телефоном, который ' \
                      f'уже используется другим пользователем {{}}'

        with mock.patch(self.sms_send_method) as sender_mock:
            request_body = {
                'phone_number': existent_user.phone_number
            }
            response = client.post(self.url, data=request_body)

            assert response.status_code == 400, \
                msg_pattern.format('HTTP статус ответа не равен 400')

            response_data = response.json()

            assert response_data.get('status') == 400002, \
                msg_pattern.format('статус бизнес-логики не равен 400002')

            assert not sender_mock.called, \
                msg_pattern.format('отправляется СМС')

            response_body = response_data.get('body')
            actual_msg = response_body.get('message')
            assert actual_msg == _('A user with that phone already exists.'), \
                msg_pattern.format('ответ содержит неверное сообщение')

    @pytest.mark.django_db(transaction=True)
    def test_sms_sending_error(self, client, sms_sending_exception,
                               valid_phone_number):

        msg_pattern = f'При POST запросе {self.url} с неработающим бэкэндом ' \
                      f'отправки СМС {{}}'

        with mock.patch(self.sms_send_method, side_effect=sms_sending_exception):
            request_body = {
                'phone_number': valid_phone_number
            }
            response = client.post(self.url, data=request_body)

            assert response.status_code == 500, \
                msg_pattern.format('HTTP статус ответа не равен 500')

            response_data = response.json()

            assert response_data.get('status') == 500001, \
                msg_pattern.format('статус бизнес-логики не равен 500001')

            response_body = response_data.get('body')
            actual_msg = response_body.get('message')
            assert actual_msg == _('Error in sending verification code.'), \
                msg_pattern.format('ответ содержит неверное сообщение')


class TestSecurityCodeVerification:

    url = '/api/v1/phone/verify/'

    @pytest.mark.django_db(transaction=True)
    def test_valid_security_code(self, client, valid_verification_data):
        msg_pattern = f'При POST запросе {self.url} с верным кодом ' \
                      f'подтверждения {{}}'
        response = client.post(self.url, data=valid_verification_data)
        assert response.status_code == 200, \
            msg_pattern.format('HTTP статус ответа не равен 200')

        response_data = response.json()
        assert response_data.get('status') == 200000, \
            msg_pattern.format('статус бизнес-логики не равен 200000')

        response_body = response_data.get('body')
        actual_msg = response_body.get('message')
        assert actual_msg == _('Security code is valid.'), \
            msg_pattern.format('ответ содержит неверное сообщение')

    @pytest.mark.django_db(transaction=True)
    def test_invalid_verification_data(self, client, invalid_verification_data):
        msg_pattern = f'При POST запросе {self.url} с неверным кодом ' \
                      f'подтверждения {{}}'
        response = client.post(self.url, data=invalid_verification_data)
        assert response.status_code == 400, \
            msg_pattern.format('HTTP статус ответа не равен 400')

        response_data = response.json()
        assert response_data.get('status') == 400003, \
            msg_pattern.format('статус бизнес-логики не равен 400003')

        response_body = response_data.get('body')
        actual_msg = response_body.get('message')
        assert actual_msg == _('Security code is not valid.'), \
            msg_pattern.format('ответ содержит неверное сообщение')


class TestSignup:

    url = '/api/v1/phone/signup/'

    @pytest.mark.django_db(transaction=True)
    def test_successful_signup(self, client, valid_signup_data):
        msg_pattern = f'При POST запросе {self.url} с корректными данными {{}}'

        response = client.post(self.url, data=valid_signup_data)
        assert response.status_code == 201, \
            msg_pattern.format('HTTP статус ответа не равен 201')

        response_data = response.json()
        assert response_data.get('status') == 201000, \
            msg_pattern.format('статус бизнес-логики не равен 201000')

        response_body = response_data.get('body')
        actual_msg = response_body.get('message')
        assert actual_msg == _('User account has been created.'), \
            msg_pattern.format('ответ содержит неверное сообщение')

    @pytest.mark.django_db(transaction=True)
    def test_invalid_verification_data(self, client,
                                       signup_data_invalid_verification):
        msg_pattern = f'При POST запросе {self.url} с неверным кодом ' \
                      f'подтверждения {{}}'
        response = client.post(self.url, data=signup_data_invalid_verification)
        assert response.status_code == 400, \
            msg_pattern.format('HTTP статус ответа не равен 400')

        response_data = response.json()
        assert response_data.get('status') == 400003, \
            msg_pattern.format('статус бизнес-логики не равен 400003')

        response_body = response_data.get('body')
        actual_msg = response_body.get('message')
        assert actual_msg == _('Security code is not valid.'), \
            msg_pattern.format('ответ содержит неверное сообщение')

    @pytest.mark.django_db(transaction=True)
    def test_invalid_registration_data(self, client, signup_data_invalid_username):
        msg_pattern = f'При POST запросе {self.url} с некорректным username {{}}'
        response = client.post(self.url, data=signup_data_invalid_username)
        assert response.status_code == 400, \
            msg_pattern.format('HTTP статус ответа не равен 400')

        response_data = response.json()
        assert response_data.get('status') == 400004, \
            msg_pattern.format('статус бизнес-логики не равен 400004')
