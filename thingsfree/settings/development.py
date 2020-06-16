import os

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
