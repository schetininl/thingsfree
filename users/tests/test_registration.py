from unittest import mock

from phone_verify.models import SMSVerification
import pytest


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

            queryset = SMSVerification.objects.filter(
                phone_number=invalid_phone_number
            )
            assert not queryset.exists(), \
                msg_pattern.format('сгенерирован код подтверждения')

            response_body = response_data.get('body')
            assert response_body.get('message') == 'Phone number is not valid.', \
                msg_pattern.format('ответ содержит неверное сообщение')
