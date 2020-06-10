import pytest
from twilio.base.exceptions import TwilioRestException


@pytest.fixture
def sms_send_method():
    """
    Метод, который выполняет отправку СМС и который будет 'замокан'
    при тестировании
    """
    return 'phone_verify.backends.twilio.TwilioBackend.send_sms'


@pytest.fixture
def sms_sending_exception():
    """
    Исключение, генерируемое mock-объектом для тестирования неудачной
    попытки отправки СМС
    """
    return TwilioRestException


@pytest.fixture
def valid_phone_number():
    return '+79604566768'


@pytest.fixture
def invalid_phone_number():
    return 'abc123456'


@pytest.fixture
def existent_user(django_user_model):
    return django_user_model.objects.create_user(
        username='test_user',
        email='test@user.ru',
        phone_number='+79604566769',
        password='123456',
    )
