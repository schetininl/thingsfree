from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

UserModel = get_user_model()


class AuthenticationBackend(ModelBackend):
    """
    Бэкэнд для аутентификации пользователей по логину, email или телефонному
    номеру.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        search_fields = ('username', 'email', 'phone_number')
        raise_exception = kwargs.get('raise_exception', False)
        if username is None:
            for field in search_fields:
                username = kwargs.get(field)
                if username is not None:
                    search_fields = (field,)
                    break
        if username is None or password is None:
            return

        try:
            user = self.find_user(search_fields, username)
        except UserModel.DoesNotExist as err:
            if raise_exception:
                raise err
            return

        is_ok, exc = self.check_user(user, password)
        if is_ok:
            return user

        if raise_exception:
            raise exc
        
    @classmethod
    def find_user(cls, search_fields, username):
        if len(search_fields) == 1:
            user = UserModel.objects.get(**{search_fields[0]: username})
        elif len(search_fields) > 1:
            q_filter = Q(**{search_fields[0]: username})
            for field in search_fields[1:]:
                q_filter |= Q(**{field: username})
            queryset = UserModel.objects.filter(q_filter)
            if queryset.exists():
                user = queryset.first()
            else:
                raise UserModel.DoesNotExist
        else:
            raise UserModel.DoesNotExist

        return user

    def check_user(self, user, password):
        if not user.check_password(password):
            return False, AuthenticationFailed
        if not self.user_can_authenticate(user):
            return False, PermissionDenied
        return True, None
