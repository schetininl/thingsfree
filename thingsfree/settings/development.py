import os
from datetime import timedelta

from . import common

globals().update(vars(common))


DEBUG = True
SECRET_KEY = 'i&=m6nqh9l2_x9300e46bwnl!%#dd3l!9vuv^3z!yjaf9_md++'
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(common.BASE_DIR, 'db.sqlite3'),
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
}
