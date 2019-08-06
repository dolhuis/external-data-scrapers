"""
Django settings for external-data-scrapers project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""


import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Django settings
INSECURE_SECRET_KEY = 'insecure'
SECRET_KEY = os.getenv('SECRET_KEY', INSECURE_SECRET_KEY)
DEBUG = SECRET_KEY == INSECURE_SECRET_KEY

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = ('127.0.0.1', '0.0.0.0')

DATAPUNT_API_URL = os.getenv(
    'DATAPUNT_API_URL', 'https://api.data.amsterdam.nl/'
)

LOGSTASH_HOST = os.getenv('LOGSTASH_HOST', '127.0.0.1')
LOGSTASH_PORT = int(os.getenv('LOGSTASH_GELF_UDP_PORT', 12201))

# Django security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.gis',
]

THIRD_PARTY_APPS = [
    'django_extensions',
    'django_filters',

    'datapunt_api',

    'rest_framework',
    'rest_framework_gis',

    'drf_yasg'
]

DEBUG_APPS = [
    'debug_toolbar',
]

LOCAL_APPS = [
    'apps.health',
    'apps.ovfiets',
    'apps.parkeergarages',
    'apps.ov',
    'apps.ndw',
    'apps.boat_tracking',
    'apps.base',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DEBUG_MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

if DEBUG:
    INSTALLED_APPS += DEBUG_APPS
    MIDDLEWARE += DEBUG_MIDDLEWARE
    CORS_ORIGIN_ALLOW_ALL = True
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
    ]

ROOT_URLCONF = 'urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'externaldata'),
        'USER': os.getenv('DATABASE_USER', 'externaldata'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': os.getenv('DATABASE_HOST', 'database'),
        'PORT': os.getenv('DATABASE_PORT', '5432')
    }
}


# Internationalization
LANGUAGE_CODE = 'nl-NL'
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = True
USE_L10N = True
USE_TZ = True

REST_FRAMEWORK = dict(
    PAGE_SIZE=20,
    MAX_PAGINATE_BY=100,
    UNAUTHENTICATED_USER={},
    UNAUTHENTICATED_TOKEN={},
    DEFAULT_AUTHENTICATION_CLASSES=(
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ),
    DEFAULT_PAGINATION_CLASS=("datapunt_api.pagination.HALPagination",),
    DEFAULT_RENDERER_CLASSES=(
        "rest_framework.renderers.JSONRenderer",
        "datapunt_api.renderers.PaginatedCSVRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        # must be lowest!
        "rest_framework_xml.renderers.XMLRenderer",
    ),
    DEFAULT_FILTER_BACKENDS=(
        # 'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
        "django_filters.rest_framework.DjangoFilterBackend"
    ),
    COERCE_DECIMAL_TO_STRING=True,
)

# Static files (CSS, JavaScript, Images) and media files
STATIC_URL = '/externaldata/static/'
STATIC_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(BASE_DIR)), 'static'
)
MEDIA_URL = '/externaldata/media/'
MEDIA_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(BASE_DIR)), 'media'
)

# Object store / Swift
if os.getenv('SWIFT_ENABLED', 'false') == 'true':
    DEFAULT_FILE_STORAGE = 'swift.storage.SwiftStorage'
    SWIFT_USERNAME = os.getenv('SWIFT_USERNAME')
    SWIFT_PASSWORD = os.getenv('SWIFT_PASSWORD')
    SWIFT_AUTH_URL = os.getenv('SWIFT_AUTH_URL')
    SWIFT_TENANT_ID = os.getenv('SWIFT_TENANT_ID')
    SWIFT_TENANT_NAME = os.getenv('SWIFT_TENANT_NAME')
    SWIFT_REGION_NAME = os.getenv('SWIFT_REGION_NAME')
    SWIFT_CONTAINER_NAME = os.getenv('SWIFT_CONTAINER_NAME')
    SWIFT_TEMP_URL_KEY = os.getenv('SWIFT_TEMP_URL_KEY')
    SWIFT_USE_TEMP_URLS = True

# The following JWKS data was obtained in the authz project :  jwkgen -create -alg ES256   # noqa
# This is a test public/private key def and added for testing .
JWKS_TEST_KEY = """
    {
        "keys": [
            {
                "kty": "EC",
                "key_ops": [
                    "verify",
                    "sign"
                ],
                "kid": "2aedafba-8170-4064-b704-ce92b7c89cc6",
                "crv": "P-256",
                "x": "6r8PYwqfZbq_QzoMA4tzJJsYUIIXdeyPA27qTgEJCDw=",
                "y": "Cf2clfAfFuuCB06NMfIat9ultkMyrMQO9Hd2H7O9ZVE=",
                "d": "N1vu0UQUp0vLfaNeM0EDbl4quvvL6m_ltjoAXXzkI3U="
            }
        ]
    }
"""

DATAPUNT_AUTHZ = {
    'JWKS': os.getenv('PUB_JWKS', JWKS_TEST_KEY),
    'ALWAYS_OK': False,
}

# Django cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


# Django Logging settings
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "console"
        },

        'graypy': {
            'level': 'ERROR',
            'class': 'graypy.GELFHandler',
            'host': LOGSTASH_HOST,
            'port': LOGSTASH_PORT,
        },

    },
    "root": {"level": "DEBUG", "handlers": ["console"]},
    "loggers": {
        "django.db": {
            "handlers": ["console"],
            "level": "ERROR"
        },
        "django": {
            "handlers": ["console"],
            "level": "ERROR"
        },
        # Debug all batch jobs
        "doc": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        "index": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False
        },
        "search": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False
        },
        "elasticsearch": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False
        },
        "urllib3": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False
        },
        "factory.containers": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        "factory.generate": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        "requests.packages.urllib3.connectionpool": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False
        },
        # Log all unhandled exceptions
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False
        },
    },
}

TESTING = os.getenv('TESTING', False)
VERIFY_SSL = os.getenv('ADP_USE_SSL_CERT', True)

SENTRY_DSN = os.getenv('SENTRY_DSN')


WATERNET_USERNAME = os.getenv('waternet_username')
WATERNET_PASSWORD = os.getenv('waternet_password')

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        ignore_errors=['ExpiredSignatureError']
)
