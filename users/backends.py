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
            if len(search_fields) == 1:
                user = UserModel.objects.get(**{search_fields[0]: username})
            else:
                q_filter = Q(**{search_fields[0]: username})
                for field in search_fields[1:]:
                    q_filter |= Q(**{field: username})
                queryset = UserModel.objects.filter(q_filter)
                if queryset.exists():
                    user = queryset.first()
                else:
                    raise UserModel.DoesNotExist
        except UserModel.DoesNotExist as err:
            UserModel().set_password(password)
            if raise_exception:
                raise err
        else:
            if not user.check_password(password):
                if raise_exception:
                    raise AuthenticationFailed
            elif not self.user_can_authenticate(user):
                if raise_exception:
                    raise PermissionDenied
            else:
                return user
