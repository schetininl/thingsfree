import pytest


pytest_plugins = [
    'users.tests.fixtures',
]

def pytest_configure():
    pytest.wrong_msg = 'ответ содержит неверное сообщение'
    pytest.http_status_not_200 = 'HTTP статус ответа не равен 200'
    pytest.http_status_not_201 = 'HTTP статус ответа не равен 201'
    pytest.http_status_not_400 = 'HTTP статус ответа не равен 400'
    pytest.http_status_not_500 = 'HTTP статус ответа не равен 500'
