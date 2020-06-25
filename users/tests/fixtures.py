import random

from django.conf import settings
from phone_verify.services import get_sms_backend
import pytest
from rest_framework_simplejwt.tokens import RefreshToken
from twilio.base.exceptions import TwilioRestException

from users.models import SocialMedia


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
def nonexistent_user():
    """Данные несуществующего пользователя."""
    return {
        'username': 'unknown_username',
        'email': 'unknown@mail.ru',
        'phone_number': '+79001234567'
    }


@pytest.fixture
def blocked_user(django_user_model, default_password):
    """Заблокированный пользователь."""
    return django_user_model.objects.create_user(
        username='blocked_user',
        email='blocked@user.ru',
        phone_number='+79604566770',
        password=default_password,
        is_active=False
    )


@pytest.fixture
def refresh_token(existent_user):
    """Refresh-токен для существующего пользователя."""
    refresh = RefreshToken.for_user(existent_user)
    return str(refresh)



@pytest.fixture
def invalid_refresh_token(refresh_token):
    """
    Невалидный refresh-токен. Генерируется на основе валидного токена путем
    удаления одного символа.
    """
    return refresh_token[:-1]


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


@pytest.fixture
def vk_provider():
    """Имя провайдера для социальной сети ВКонтакте."""
    return 'vk-oauth2'


@pytest.fixture
def ok_provider():
    """Имя провайдера для социальной сети Одноклассники."""
    return 'odnoklassniki-oauth2'


@pytest.fixture
def fb_provider():
    """Имя провайдера для социальной сети Facebook."""
    return 'facebook'


@pytest.fixture
def random_social_provider(vk_provider, ok_provider, fb_provider):
    """Случайный провайдер социальной сети."""
    return random.choice((vk_provider, ok_provider, fb_provider))


@pytest.fixture(scope='class')
def social_providers():
    """Список социальных сетей."""
    return [
        {
            'name': 'vk-oauth2',
            'title': 'ВКонтакте',
            'url': 'http://oauth.vk.com/authorize',
            'app_id': '615687813254'
        },
        {
            'name': 'odnoklassniki-oauth2',
            'title': 'Одноклассники',
            'url': 'https://connect.ok.ru/oauth/authorize',
            'app_id': '21489731248'
        },
        {
            'name': 'facebook',
            'title': 'Facebook',
            'url': 'https://www.facebook.com/v3.2/dialog/oauth',
            'app_id': '91245786321147'
        }
    ]


@pytest.fixture
def social_providers_setup(social_providers, monkeypatch):
    """
    Создает объекты модели SocialMedia и устанавливает в настройках
    ключи приложений.
    """
    for provider in social_providers:
        social_media = SocialMedia(
            name=provider['title'],
            oauth_backend=provider['name'],
            logo='abcdef'
        )
        social_media.save()

        setting_key = 'SOCIAL_AUTH_{}_KEY'.format(
            provider['name'].replace('-', '_').upper()
        )
        monkeypatch.setattr(settings, setting_key, provider['app_id'])


@pytest.fixture(scope='class')
def valid_oauth_token():
    """Валидный OAuth токен, выданный социальной сетью"""
    return ('EAAmWwEcZCvcUBAJgown6ZB1sWLmigvbbwZAGUVmxNuDXZAihfllBUo1he6Hq8ZBkZ'
            'B5j3wfDd6HaxA6d23CIZCXhPjWZBR69IbBcXGeZAOD15zFfbutAquF7OAnROE3RfVg'
            'e3RjhtZA2NYJRS4FWc5PvcmGxr2FYmaR7gGBtL3iU0YrOXZBpZAS2Y0oLZCQS4kzED'
            'd6KVIGtaubcAY9z4NgySuW3G')


@pytest.fixture(scope='class')
def invalid_oauth_token():
    """Невалидный OAuth токен, выданный социальной сетью"""
    return ('vbbwZAGUVmxNuDXZAihfllBUo1he6Hq8ZBkZEAAmWwEcZCvcUBAJgown6ZB1sWLmig'
            'BcXGeZAOD15zFfbutAquF7OAnROE3RfVgB5j3wfDd6HaxA6d23CIZCXhPjWZBR69Ib'
            'maR7gGBtL3iU0YrOXZBpZAS2Y0oLZCQS4kzEDe3RjhtZA2NYJRS4FWc5PvcmGxr2FY'
            'AY9z4NgySuW3Gd6KVIGtaubc')


@pytest.fixture(scope='class')
def social_user_data():
    """Данные пользователей социальных сетей."""
    return {
        'vk-oauth2': {
            'id': '123456789',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'screen_name': 'id123456789',
            'nickname': 'ivanushka'
        },
        'odnoklassniki-oauth2': {
            'uid': '9876543210123',
            'first_name': 'Фидель',
            'last_name': 'Кастро',
            'name': 'Фидель Кастро',
            'email': 'cuba@mail.ru'
        },
        'facebook': {
            'id': '145698742132545',
            'first_name': 'Илья',
            'last_name': 'Муромец',
            'email': 'bogatyr@mail.ru'
        }
    }


@pytest.fixture
def mock_get_user_data(valid_oauth_token, social_user_data):
    """
    Функция-пустышка, возвращающая 'замоканные' ответы социальных сетей
    на запросы о данных профиля пользователя.
    """
    def get_json(self, url, *args, **kwargs):
        token = kwargs['params']['access_token']

        if url.startswith('https://api.vk.com/'):
            if token != valid_oauth_token:
                return {
                    'error': {
                        'error_msg': 'Unknown error',
                        'error_code': 1
                    }
                }
            return {
                'response': [social_user_data['vk-oauth2']]
            }
        elif url.startswith('https://api.ok.ru/'):
            if token != valid_oauth_token:
                return {
                    'error_code': 103,
                    'error_msg': 'Invalid session key',
                    'error_data': None
                }
            return social_user_data['odnoklassniki-oauth2']
        elif url.startswith('https://graph.facebook.com/'):
            if token != valid_oauth_token:
                return None
            return social_user_data['facebook']
        return None

    return get_json
