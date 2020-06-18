import pytest
from rest_framework_simplejwt.tokens import AccessToken


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

        validated_token = AccessToken(access_token)
        assert validated_token['username'] == existent_user.username, \
            msg_pattern.format('в теле ответа содержится неверный токен доступа')
