from unittest import mock

from phone_verify.models import SMSVerification
import pytest


class TestSecurityCodeSending:

    @pytest.mark.django_db(transaction=True)
    def test_successful_sending(self, client, valid_phone_number):

        url = '/api/v1/phone/register/'
        msg_pattern = f'При POST запросе {url} с валидными данными {{}}'

        with mock.patch(
                'phone_verify.backends.twilio.TwilioBackend.send_sms'
        ) as sender_mock:

            request_body = {
                'phone_number': valid_phone_number
            }
            response = client.post(url, data=request_body)

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
