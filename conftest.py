import pytest


pytest_plugins = [
    'users.tests.fixtures',
]


def pytest_configure():
    pytest.msg = {
        'wrong_http_status': 'неверный HTTP статус ответа',
        'wrong_app_status': 'неверный статус бизнес-логики',
        'wrong_message': 'ответ содержит неверное сообщение',
        'no_token': 'в теле ответа не содержится токен доступа',
        'no_token_life': 'в теле ответа не содержится время жизни токена',
        'no_refresh_token': 'в теле ответа не содежится refresh-токен',
    }
