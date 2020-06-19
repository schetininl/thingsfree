import pytest
from django.utils.translation import gettext_lazy as _


class TestTokenObtain:
    """Набор тестов для тестирования выдачи JWT-токенов."""

    url = '/api/v1/token/'

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('user_field', ['username', 'email', 'phone_number'])
    def test_successful_obtain(self, client, existent_user, default_password, user_field):
        msg_pattern = f'При POST запросе {self.url} с валидными данными {{}}'

        request_body = {
            'user': getattr(existent_user, user_field),
            'password': default_password
        }
        response = client.post(self.url, data=request_body)

        assert response.status_code == 200, \
            msg_pattern.format(pytest.http_status_not_200)

        response_data = response.json()

        assert response_data.get('status') == 200000, \
            msg_pattern.format('статус бизнес-логики не равен 200000')

        response_body = response_data.get('body')
        access_token = response_body.get('access', '')
        refresh_token = response_body.get('refresh', '')
        assert access_token != '', \
            msg_pattern.format('в теле ответа не содержится токен доступа')
        assert refresh_token != '', \
            msg_pattern.format('в теле ответа не содержится refresh-токен')

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('user_field', ['username', 'email', 'phone_number'])
    def test_nonexistent_user(self, client, nonexistent_user, default_password, user_field):
        msg_pattern = f'При POST запросе {self.url} с данными несуществующего' \
                      f' пльзователя {{}}'

        request_body = {
            'user': nonexistent_user[user_field],
            'password': default_password
        }
        response = client.post(self.url, data=request_body)
        assert response.status_code == 400, \
            msg_pattern.format(pytest.http_status_not_400)

        response_data = response.json()

        assert response_data.get('status') == 400005, \
            msg_pattern.format('статус бизнес-логики не равен 400005')

        response_body = response_data.get('body')
        actual_msg = response_body.get('message')
        assert actual_msg == _('User not found.'), \
            msg_pattern.format(pytest.wrong_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('user_field', ['username', 'email', 'phone_number'])
    def test_wrong_password(self, client, existent_user, default_password, user_field):
        msg_pattern = f'При POST запросе {self.url} с неверным паролем {{}}'

        request_body = {
            'user': getattr(existent_user, user_field),
            'password': default_password + '1'
        }
        response = client.post(self.url, data=request_body)

        assert response.status_code == 400, \
            msg_pattern.format(pytest.http_status_not_400)

        response_data = response.json()

        assert response_data.get('status') == 400006, \
            msg_pattern.format('статус бизнес-логики не равен 400006')

        response_body = response_data.get('body')
        actual_msg = response_body.get('message')
        assert actual_msg == _('Wrong password.'), \
            msg_pattern.format(pytest.wrong_msg)

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('user_field', ['username', 'email', 'phone_number'])
    def test_blocked_user(self, client, blocked_user, default_password, user_field):
        msg_pattern = f'При POST запросе {self.url} с данными ' \
                      f'заблокированного пользователя {{}}'

        request_body = {
            'user': getattr(blocked_user, user_field),
            'password': default_password
        }
        response = client.post(self.url, data=request_body)

        assert response.status_code == 400, \
            msg_pattern.format(pytest.http_status_not_400)

        response_data = response.json()

        assert response_data.get('status') == 400007, \
            msg_pattern.format('статус бизнес-логики не равен 400007')

        response_body = response_data.get('body')
        actual_msg = response_body.get('message')
        assert actual_msg == _('The user is blocked.'), \
            msg_pattern.format(pytest.wrong_msg)


class TestTokenRefresh:
    """Набор тестов для тестирования обновления токена доступа."""

    url = '/api/v1/token/refresh/'

    @pytest.mark.django_db(transaction=True)
    def test_successful_refresh(self, client, refresh_token):
        msg_pattern = f'При POST запросе {self.url} с валидными данными {{}}'

        request_body = {
            'refresh': refresh_token
        }
        response = client.post(self.url, data=request_body)

        assert response.status_code == 200, \
            msg_pattern.format(pytest.http_status_not_200)

        response_data = response.json()

        assert response_data.get('status') == 200000, \
            msg_pattern.format('статус бизнес-логики не равен 200000')

        response_body = response_data.get('body')
        access_token = response_body.get('access', '')
        assert access_token != '', \
            msg_pattern.format('в теле ответа не содержится токен доступа')

    @pytest.mark.django_db(transaction=True)
    def test_invalid_refres_token(self, client, invalid_refresh_token):
        msg_pattern = f'При POST запросе {self.url} с невалидными данными {{}}'

        request_body = {
            'refresh': invalid_refresh_token
        }
        response = client.post(self.url, data=request_body)

        assert response.status_code == 400, \
            msg_pattern.format(pytest.http_status_not_400)

        response_data = response.json()

        assert response_data.get('status') == 400008, \
            msg_pattern.format('статус бизнес-логики не равен 400008')

        response_body = response_data.get('body')
        actual_msg = response_body.get('message')
        assert actual_msg == _('Invalid refresh-token.'), \
            msg_pattern.format(pytest.wrong_msg)
