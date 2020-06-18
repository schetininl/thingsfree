from phone_verify.services import get_sms_backend
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
    """Валидный телефонный номер."""
    return '+79604566768'


@pytest.fixture
def invalid_phone_number():
    """Невалидный телефонный номер."""
    return 'abc123456'


@pytest.fixture
def default_password():
    """Пароль для создаваемых пользователей."""
    return '123456'


@pytest.fixture
def existent_user(django_user_model, default_password):
    """Имеющийся в базе данных пользователь."""
    return django_user_model.objects.create_user(
        username='test_user',
        email='test@user.ru',
        phone_number='+79604566769',
        password=default_password,
    )


@pytest.fixture
def valid_verification_data(valid_phone_number):
    """Корректные данные для подтверждения телефонного номера."""
    sms_backend = get_sms_backend(valid_phone_number)
    security_code, session_token = sms_backend\
        .create_security_code_and_session_token(valid_phone_number)

    return {
        'phone_number': valid_phone_number,
        'security_code': security_code,
        'session_token': session_token
    }


@pytest.fixture(params=('security_code', 'session_token', 'phone_number'))
def invalid_verification_data(request, valid_verification_data):
    """
    Неверные данные для подтверждения телефонного номера.
    Для генерации используются корректные данные, в которых заменяется один
    символ.
    Генерируются три варианта:
    1) неверный код подтверждения
    2) неверный токен сессии
    3) неверный номер телефона
    """
    invalid_field = valid_verification_data.get(request.param)
    invalid_field = chr(ord(invalid_field[-1]) + 1) + invalid_field[:-1]
    invalid_verification_data = valid_verification_data.copy()
    invalid_verification_data[request.param] = invalid_field

    return invalid_verification_data


@pytest.fixture
def valid_signup_data(valid_verification_data):
    """Корректные данные для регистрации нового аккаунта."""
    return {
        **valid_verification_data,
        'username': 'test_user',
        'password': '123456'
    }


@pytest.fixture
def signup_data_invalid_verification(invalid_verification_data):
    """
    Некорректные данные для регистрации нового аккаунта с неверными данными
    для подтверждения номера телефона.
    """
    return {
        **invalid_verification_data,
        'username': 'test_user',
        'password': '123456'
    }


@pytest.fixture(params=('test' * 40, 'test_user'),
                ids=('too long username', 'not unique username'))
def signup_data_invalid_username(request, existent_user, valid_verification_data):
    """
    Некорректные данные для регистрации нового аккаунта с некорректным логином.
    Генерируются следующие варианты:
    1) слишком длинный логин - более 150 символов
    2) неуникальный логин
    """
    return {
        **valid_verification_data,
        'username': request.param,
        'password': '123456'
    }
