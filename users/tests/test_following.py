from itertools import cycle

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


class TestFollowersList:
    """Набор тестов для получения списка подписчиков пользователя."""

    def get(self, client, user_id, params=None):
        response = client.get(f'/api/v1/users/{user_id}/followers/', data=params)
        response_data = response.json()
        response_body = response_data.get('body', {})
        app_status = response_data.get('status', 0)

        return response.status_code, app_status, response_body

    def test_user_followers(self, client, users_with_following):
        msg_pattern = f'При POST запросе /api/v1/users/user_id/followers/ {{}}'

        query_params_cycle = cycle([
            None,
            {'limit': 5, 'offset': 0},
            {'limit': 5, 'offset': 2},
            {'limit': 100, 'offset': 0},
            {'limit': 5, 'offset': 100}
        ])

        for user, followers, _ in users_with_following:
            query_params = next(query_params_cycle)
            http_status, app_status, response_body = self.get(
                client,
                user.id,
                query_params
            )

            assert http_status == 200, msg_pattern.format(
                pytest.msg['wrong_http_status'])
            assert app_status == 200000, msg_pattern.format(
                pytest.msg['wrong_app_status'])

            count_of_followers = len(followers)
            assert response_body['count'] == count_of_followers, \
                msg_pattern.format('в поле ответа count неверное значение')

            if query_params is None:
                expected_retrieve_size = count_of_followers
            else:
                expected_retrieve_size = min(
                    max(count_of_followers - query_params['offset'], 0),
                    query_params['limit']
                )

            assert len(response_body['results']) == expected_retrieve_size, \
                msg_pattern.format('неверный размер выборки в ответе')

            for result_item in response_body['results']:
                follower = User.objects.get(pk=result_item['id'])

                assert follower in followers, msg_pattern.format(
                    'ответ содержит неверный список подписчиков')

                assert (result_item['username'] == follower.username and
                        result_item['first_name'] == follower.first_name and
                        result_item['last_name'] == follower.last_name), \
                    msg_pattern.format('ответ содержит неверные данные подписчиков')

    def test_authorized_user_followers(self, existent_user, user_client,
                                       authorized_user_followers):
        msg_pattern = f'При POST запросе /api/v1/users/me/followers/ {{}}'

        http_status, app_status, response_body = self.get(user_client, 'me')

        assert http_status == 200, msg_pattern.format(
            pytest.msg['wrong_http_status'])
        assert app_status == 200000, msg_pattern.format(
            pytest.msg['wrong_app_status'])

        count_of_followers = len(authorized_user_followers)
        assert response_body['count'] == count_of_followers, \
            msg_pattern.format('в поле ответа count неверное значение')
        assert len(response_body['results']) == count_of_followers, \
            msg_pattern.format('неверный размер выборки в ответе')

        for result_item in response_body['results']:
            follower = User.objects.get(pk=result_item['id'])

            assert follower in authorized_user_followers, msg_pattern.format(
                'ответ содержит неверный список подписчиков')
