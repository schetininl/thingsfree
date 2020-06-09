import pytest


@pytest.fixture
def sms_send_method():
    """
    Метод, который выполняет отправку СМС и который будет 'замокан'
    при тестировании
    """
    return 'phone_verify.backends.twilio.TwilioBackend.send_sms'


@pytest.fixture
def valid_phone_number():
    return '+79604566768'


@pytest.fixture
def invalid_phone_number():
    return 'abc123456'
