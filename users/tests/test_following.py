import uuid

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestFollowersList:
    """Набор тестов для получения списка подписчиков пользователя."""

    def get(self, client, user_id, params=None):
        response = client.get(f'/api/v1/users/{user_id}/followers/', data=params)
        response_data = response.json()
        response_body = response_data.get('body', {})
        app_status = response_data.get('status', 0)

        return response.status_code, app_status, response_body

    def test_user_followers(self, client, users_with_following,
                            limit_offset_combinations):
        msg_pattern = f'При GET запросе /api/v1/users/user_id/followers/ {{}}'

        for user, followers, _ in users_with_following:
            query_params = next(limit_offset_combinations)
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
        msg_pattern = f'При GET запросе /api/v1/users/me/followers/ {{}}'

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

    def test_unauthorized_user_followers(self, client):
        msg_pattern = f'При GET запросе /api/v1/users/me/followers/ ' \
                      f'без токена доступа {{}}'

        http_status, app_status, response_body = self.get(client, 'me')

        assert http_status == 401, msg_pattern.format(
            pytest.msg['wrong_http_status'])
        assert app_status == 401000, msg_pattern.format(
            pytest.msg['wrong_app_status'])


@pytest.mark.django_db(transaction=True)
class TestFollowingList:
    """Набор тестов для получения списка подписок пользователя."""

    def get(self, client, user_id, params=None):
        response = client.get(f'/api/v1/users/{user_id}/following/', data=params)
        response_data = response.json()
        response_body = response_data.get('body', {})
        app_status = response_data.get('status', 0)

        return response.status_code, app_status, response_body

    def test_user_following(self, client, users_with_following,
                            limit_offset_combinations):
        msg_pattern = f'При GET запросе /api/v1/users/user_id/following/ {{}}'

        for user, _, authors in users_with_following:
            query_params = next(limit_offset_combinations)
            http_status, app_status, response_body = self.get(
                client,
                user.id,
                query_params
            )

            assert http_status == 200, msg_pattern.format(
                pytest.msg['wrong_http_status'])
            assert app_status == 200000, msg_pattern.format(
                pytest.msg['wrong_app_status'])

            count_of_authors = len(authors)
            assert response_body['count'] == count_of_authors, \
                msg_pattern.format('в поле ответа count неверное значение')

            if query_params is None:
                expected_retrieve_size = count_of_authors
            else:
                expected_retrieve_size = min(
                    max(count_of_authors - query_params['offset'], 0),
                    query_params['limit']
                )

            assert len(response_body['results']) == expected_retrieve_size, \
                msg_pattern.format('неверный размер выборки в ответе')

            for result_item in response_body['results']:
                author = User.objects.get(pk=result_item['id'])

                assert author in authors, msg_pattern.format(
                    'ответ содержит неверный список подписок')

                assert (result_item['username'] == author.username and
                        result_item['first_name'] == author.first_name and
                        result_item['last_name'] == author.last_name), \
                    msg_pattern.format('ответ содержит неверные данные авторов')

    def test_authorized_user_following(self, existent_user, user_client,
                                       authorized_user_following):
        msg_pattern = f'При GET запросе /api/v1/users/me/following/ {{}}'

        http_status, app_status, response_body = self.get(user_client, 'me')

        assert http_status == 200, msg_pattern.format(
            pytest.msg['wrong_http_status'])
        assert app_status == 200000, msg_pattern.format(
            pytest.msg['wrong_app_status'])

        count_of_authors = len(authorized_user_following)
        assert response_body['count'] == count_of_authors, \
            msg_pattern.format('в поле ответа count неверное значение')
        assert len(response_body['results']) == count_of_authors, \
            msg_pattern.format('неверный размер выборки в ответе')

        for result_item in response_body['results']:
            author = User.objects.get(pk=result_item['id'])

            assert author in authorized_user_following, msg_pattern.format(
                'ответ содержит неверный список подписок')

    def test_unauthorized_user_following(self, client):
        msg_pattern = f'При GET запросе /api/v1/users/me/following/ ' \
                      f'без токена доступа {{}}'

        http_status, app_status, response_body = self.get(client, 'me')

        assert http_status == 401, msg_pattern.format(
            pytest.msg['wrong_http_status'])
        assert app_status == 401000, msg_pattern.format(
            pytest.msg['wrong_app_status'])


@pytest.mark.django_db(transaction=True)
class TestFollowChange:
    """Набор тестов для создания и удаления подписок."""

    def post(self, action, client, user_id):
        response = client.post(f'/api/v1/users/{user_id}/{action}/')
        response_data = response.json()
        response_body = response_data.get('body', {})
        app_status = response_data.get('status', 0)

        return response.status_code, app_status, response_body

    def test_follow(self, existent_user, user_client, user_generator):
        msg_pattern = f'При POST запросе /api/v1/users/user_id/follow/ {{}}'

        author = next(user_generator)
        http_status, app_status, response_body = self.post(
            'follow',
            user_client,
            author.id
        )

        assert http_status == 200, msg_pattern.format(
            pytest.msg['wrong_http_status'])
        assert app_status == 200000, msg_pattern.format(
            pytest.msg['wrong_app_status'])

        assert existent_user.following.count() == 1, msg_pattern.format(
            'не создается подписка')

        following = existent_user.following.first()
        assert (following.author == author and
                following.follower == existent_user), msg_pattern.format(
            'создается подписка с неверными данными')

    def test_follow_myself(self, existent_user, user_client):
        msg_pattern = f'При попытке выполнить подписку на самого себя {{}}'

        http_status, app_status, response_body = self.post(
            'follow',
            user_client,
            existent_user.id
        )

        assert http_status == 400, msg_pattern.format(
            pytest.msg['wrong_http_status'])
        assert app_status == 400013, msg_pattern.format(
            pytest.msg['wrong_app_status'])

        assert existent_user.following.count() == 0, msg_pattern.format(
            'создается ненужная подписка')

    def test_following_exists(self, existent_user, user_client,
                              authorized_user_following):
        msg_pattern = f'При попытке подписаться на пользователя, на которого ' \
                      f'уже выполнена подписка {{}}'

        http_status, app_status, response_body = self.post(
            'follow',
            user_client,
            authorized_user_following[0].id
        )

        assert http_status == 400, msg_pattern.format(
            pytest.msg['wrong_http_status'])
        assert app_status == 400011, msg_pattern.format(
            pytest.msg['wrong_app_status'])

    def test_follow_blocked_user(self, user_client, existent_user, blocked_user):
        msg_pattern = f'При попытке подписаться на заблокированного пользователя {{}}'

        http_status, app_status, response_body = self.post(
            'follow',
            user_client,
            blocked_user.id
        )

        assert http_status == 400, msg_pattern.format(
            pytest.msg['wrong_http_status'])
        assert app_status == 400007, msg_pattern.format(
            pytest.msg['wrong_app_status'])

        assert existent_user.following.count() == 0, msg_pattern.format(
            'создается ненужная подписка')

    def test_unauthorized_follow(self, client, existent_user):
        msg_pattern = f'При POST запросе /api/v1/users/user_id/follow/ ' \
                      f'без токена доступа {{}}'

        http_status, app_status, response_body = self.post(
            'follow',
            client,
            existent_user.id
        )

        assert http_status == 401, msg_pattern.format(
            pytest.msg['wrong_http_status'])
        assert app_status == 401000, msg_pattern.format(
            pytest.msg['wrong_app_status'])

        assert existent_user.followers.count() == 0, msg_pattern.format(
            'создается ненужная подписка')

    def test_follow_nonexistant_user(self, user_client, existent_user):
        msg_pattern = f'При попытке подписаться на несуществующего пользователя {{}}'

        http_status, app_status, response_body = self.post(
            'follow',
            user_client,
            uuid.uuid4()
        )

        assert http_status == 404, msg_pattern.format(
            pytest.msg['wrong_http_status'])
        assert app_status == 404000, msg_pattern.format(
            pytest.msg['wrong_app_status'])

        assert existent_user.followers.count() == 0, msg_pattern.format(
            'создается ненужная подписка')

    def test_unfollow(self, user_client, existent_user, authorized_user_following):
        msg_pattern = f'При POST запросе /api/v1/users/user_id/unfollow/ {{}}'

        for author in authorized_user_following:
            http_status, app_status, response_body = self.post(
                'unfollow',
                user_client,
                author.id
            )

            assert http_status == 200, msg_pattern.format(
                pytest.msg['wrong_http_status'])
            assert app_status == 200000, msg_pattern.format(
                pytest.msg['wrong_app_status'])

        assert existent_user.following.count() == 0, msg_pattern.format(
            'не удаляются подписки')

    def test_remove_nonexistent_following(self, user_client, existent_user,
                                          user_generator):
        msg_pattern = f'При попытке удаления несуществующей подписки {{}}'

        author = next(user_generator)
        http_status, app_status, response_body = self.post(
            'unfollow',
            user_client,
            author.id
        )

        assert http_status == 400, msg_pattern.format(
            pytest.msg['wrong_http_status'])
        assert app_status == 400012, msg_pattern.format(
            pytest.msg['wrong_app_status'])

    def test_unauthorized_unfollow(self, client, existent_user):
        msg_pattern = f'При POST запросе /api/v1/users/user_id/unfollow/ ' \
                      f'без токена доступа {{}}'

        http_status, app_status, response_body = self.post(
            'unfollow',
            client,
            existent_user.id
        )

        assert http_status == 401, msg_pattern.format(
            pytest.msg['wrong_http_status'])
        assert app_status == 401000, msg_pattern.format(
            pytest.msg['wrong_app_status'])

    def test_unfollow_nonexistent_user(self, user_client):
        msg_pattern = f'При попытке удалить подписку на несуществующего пользователя {{}}'

        http_status, app_status, response_body = self.post(
            'unfollow',
            user_client,
            uuid.uuid4()
        )

        assert http_status == 404, msg_pattern.format(
            pytest.msg['wrong_http_status'])
        assert app_status == 404000, msg_pattern.format(
            pytest.msg['wrong_app_status'])
