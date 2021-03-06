"""
Django settings for wat project.

Generated by 'django-admin startproject' using Django 2.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import os
import sys

import environ

env = environ.Env()
root = environ.Path(__file__) - 2

env.read_env(root('../config/default.env'))

if sys.argv[0][-9:] == "manage.py" or sys.argv[0][-10:] == "console.py":
    env.read_env(root('../config/manage.py.env'))
    MANAGE_COMMAND = True
else:
    MANAGE_COMMAND = False

if env.bool("DEBUGGER_CONFIG", default=False) or len(sys.argv) > 1 and sys.argv[1] == "runserver":
    MANAGE_COMMAND = False
    env.read_env(root('../config/debugserver.env'))

# config for pycharm started tasks
executable = sys.argv[0].split("/")
if len(executable) > 2 and executable[-2] == "pycharm":
    env.read_env(root('../config/debugserver.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

DEBUG = env('DEBUG', default=False)

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'raven.contrib.django.raven_compat',
    'django_celery_beat',
    'semanticuiforms',
    'simplemde',
    'wot_ui',
    'wot_user',
    'wat_test',
    'wot_api',
    'wot_index',
    'wot_web_wtr',
    'wot_admin_tools',
    'wot_banner'
]

if MANAGE_COMMAND:
    INSTALLED_APPS.append('django_extensions')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DEBUG_TOOLBAR = False
if DEBUG:
    DEBUG_TOOLBAR = True
    INTERNAL_IPS = ['127.0.0.1']
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

ROOT_URLCONF = 'wat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wot_ui.context_processor.const_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'wat.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASE_URL = env.str("DATABASE_URL", default=None)

DATABASES = {
    'default': env.db(),
}

if not DEBUG:
    CONN_MAX_AGE = 600

# Caches

CACHES = {
    'default': env.cache("REDIS_URL", default="dummycache://"),
    'local': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = root('staticfiles/')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

AUTH_USER_MODEL = 'wot_user.User'

AUTHENTICATION_BACKENDS = (
    'wot_user.auth_backend.WorldOfTanksSimpleAuth',
)

if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_PRELOAD = True

PROJECT_VERSION = env.str("PROJECT_VERSION", default=None)

RAVEN_URL = env.str("RAVEN_URL", default=None)
if RAVEN_URL:
    RAVEN_CONFIG = {
        'dsn': RAVEN_URL,
        # If you are using git, you can also automatically configure the
        # release based on the git info.
        # 'release': raven.fetch_git_sha(os.path.abspath(os.pardir)),
    }
    if PROJECT_VERSION:
        RAVEN_CONFIG['release'] = PROJECT_VERSION

CELERY_BROKER_URL = env.str("REDIS_URL")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_RESULT_BACKEND = env.str("REDIS_URL")
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_DEFAULT_QUEUE = "default"

if DEBUG and False:
    print("Celery always eager!")
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

WARGAMING_TOKEN = env.str("WARGAMING_TOKEN", default=None)

WOT_ADMIN_USERS = env.list("WOT_ADMIN_USERS", default=[])
WOT_CLAN = env.int("WOT_CLAN", default=None)

PROJECT_TITLE = env.str("PROJECT_TITLE", default="HelloWorld")

MEDIA_ROOT = env.str("MEDIA_ROOT", default=None)


def skip_static_requests(record):
    if record.args[0].startswith('GET /static/'):
        return False
    return True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(module)12s %(levelname)s %(message)s'
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'skip_static_requests': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_static_requests
        }
    },
    'handlers': {
        'django.server': {
            'level': 'INFO',
            'filters': ['skip_static_requests'],
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'logging'},
            'formatter': 'verbose',
        },
        'sentry_info': {
            'level': 'INFO',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'logging'},
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['console', 'sentry'],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'sentry'],
            'propagate': True,
        },
        'hummel': {
            'handlers': ['console', 'sentry_info'],
            'level': 'INFO',
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },

    }
}
