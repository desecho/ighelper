"""
Django settings for ighelper_project project.

Generated by 'django-admin startproject' using Django 2.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import os.path as op
import sys

import raven

try:
    import local_settings
except ImportError:
    try:
        from . import initial_settings as local_settings
    except ImportError:  # pragma: no cover
        print('No initial settings!')
        sys.exit()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Debugging
DEBUG = local_settings.DEBUG
INTERNAL_IPS = local_settings.INTERNAL_IPS

DATABASES = local_settings.DATABASES
WSGI_APPLICATION = 'ighelper_project.wsgi.application'
ROOT_URLCONF = 'ighelper_project.urls'
SECRET_KEY = local_settings.SECRET_KEY
ALLOWED_HOSTS = [local_settings.PROJECT_DOMAIN]
SESSION_SAVE_EVERY_REQUEST = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Custom
    'raven.contrib.django.raven_compat',
    'admin_reorder',
    'menu',
    'rosetta',
    'ighelper',
]
if DEBUG:  # pragma: no cover
    INSTALLED_APPS += [
        'debug_toolbar',
        'template_timings_panel',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]
if DEBUG:  # pragma: no cover
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

# Logging
if not DEBUG:  # pragma: no cover
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': ('%(levelname)s %(asctime)s %(module)s '
                           '%(process)d %(thread)d %(message)s')
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
                'tags': {
                    'custom-tag': 'x'
                },
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (os.path.join(BASE_DIR, 'templates'), ),
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Custom
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                # IGHelper
                'ighelper.context_processors.variables',
            ],
        },
    },
]
if DEBUG:  # pragma: no cover
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]

# Static files
STATIC_ROOT = op.join(local_settings.PROJECT_ROOT, 'static')
STATIC_URL = '/static/'

# Media files
MEDIA_ROOT = op.join(local_settings.PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

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

AUTH_USER_MODEL = 'ighelper.User'
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', )

# Internationalization
LANGUAGE_CODE = 'en'
USE_I18N = True
USE_L10N = True
LANGUAGES = (
    ('en', 'English'),
    ('ru', 'Русский'),
)
LOCALE_PATHS = (op.join(local_settings.PROJECT_ROOT, 'project', 'locale'), )

# Timezone
TIME_ZONE = 'US/Eastern'
USE_TZ = True

# Login
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# --== Modules settings ==--

# django-modeladmin-reorder
ADMIN_REORDER = ({
    'app': 'ighelper',
    'models': ('ighelper.User', 'ighelper.Media', 'ighelper.Follower', 'ighelper.Like')
}, )

# raven
RAVEN_CONFIG = {
    'dsn': local_settings.RAVEN_DSN,
    'release': raven.fetch_git_sha(local_settings.GIT_ROOT),
}

# django-debug-toolbar
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
    # django-debug-toolbar-template-timings
    'template_timings_panel.panels.TemplateTimings.TemplateTimings',
]

# --== Project settings ==--

ADMIN_EMAIL = local_settings.ADMIN_EMAIL
INSTAGRAM_BASE_URL = 'https://www.instagram.com'
DESECHO8653_USERNAME = 'desecho8653'
DESECHO8653_PASSWORD = local_settings.DESECHO8653_PASSWORD

# This is here to fix the problem with static files on dev
try:
    from local_settings2 import *  # noqa pylint: disable=wildcard-import
except ImportError:
    pass
