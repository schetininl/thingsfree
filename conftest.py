import pytest


pytest_plugins = [
    'users.tests.fixtures',
]

def pytest_configure():
    pytest.wrong_msg = 'ответ содержит неверное сообщение'
    pytest.no_token = 'в теле ответа не содержится токен доступа'
    pytest.no_token_lifetime = 'в теле ответа не содержится время жизни токена'
    pytest.no_refresh_token = 'в теле ответа не содежится refresh-токен'

    for code in (200, 201, 400, 401, 500):
        setattr(
            pytest,
            f'http_status_not_{code}',
            f'HTTP статус ответа не равен {code}'
        )
    for code in (200000, 201000, 400003):
        setattr(
            pytest,
            f'app_status_not_{code}',
            f'статус бизнес-логики не равен {code}'
        )
