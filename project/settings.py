"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 4.2.17.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path

from dotenv_ import (EMAIL_HOST_PASSWORD_, EMAIL_HOST_USER_, POSTGRES_DB,
                     POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_PORT,
                     POSTGRES_USER, SECRET_KEY_)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY_

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
]


# Application definition

INSTALLED_APPS = [
    "corsheaders",
    "bootstrap4",
    "rest_framework",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "webpack_loader",
    "cloud_user",
    "cloud_file",
    "cloud",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "project.csrf.CustomCsrfMiddleware",
]
# From MIDDLEWARE = []
# https://docs.djangoproject.com/en/4.2/ref/middleware/#django.middleware.cache.FetchFromCacheMiddleware
# 'django.middleware.cache.FetchFromCacheMiddleware',

# REST_FRAMEWORK = {
# 'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',
#     ]
# Use Django's standard `django.contrib.auth` permissions,
# or allow read-only access for unauthenticated users.
# 'DEFAULT_PERMISSION_CLASSES': [
#     'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
# ],
# 'PAGE_SIZE': 10,
# }
ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates/"),
            # os.path.join(BASE_DIR, 'cloud_file/templates/'),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": POSTGRES_DB,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "HOST": POSTGRES_HOST,
        "PORT": POSTGRES_PORT,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ru"

TIME_ZONE = "Asia/Novosibirsk"

USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
MIGRATION_MODULES = {
    "cloud_user": "cloud_user.migrations",
    "cloud_file": "cloud_file.migrations",
    # 'cloud': 'cloud.migrations',
}
STATICFILES_DIRS = [
    # ("cloud_user_static", os.path.join(BASE_DIR, "cloud_user\\static")),
    # "/app/cloud_user/static",
]

STATIC_ROOT = os.path.join(BASE_DIR,  "static")
STATIC_URL = os.environ.get("STATIC_URL", "static/")
# STATIC_URL = "static/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
# MEDIA_ROOT = "/media/"


# MEDIA_URL = 'media/'
#

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DEFAULT_CHARSET = "utf-8"

AUTH_USER_MODEL = "cloud_user.UserRegister"


# WEBPACK
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        # 'BUNDLE_DIR_NAME': '..\\frontend\\src\\bundles',
        "BUNDLE_DIR_NAME": "cloud_user\\static\\bundles",
        "STATS_FILE": os.path.join(
            BASE_DIR, "cloud_user\\static\\bundles\\webpack-stats.json"
        ),

        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "TEST": {
            "NAME": "test_cloud",
        },
        "IGNORE": [
            # '.+\.map$'
            r".+\.hot-update.js",
            r".+\.map",
        ],
        "LOADER_CLASS": "webpack_loader.loader.WebpackLoader",
    }
}
# if not DEBUG:
#     WEBPACK_LOADER['DEFAULT'].update({
#         'BUNDLE_DIR_NAME': 'bundles\\',
#         'STATS_FILE': os.path.join(BASE_DIR, 'bundles\\webpack-stats.json')
#     })
#
# '''Logging'''
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

# EMAIL_BACKEND in down for a product
# https://docs.djangoproject.com/en/4.2/topics/email/#smtp-backend
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_BACKEND in down for a development

# https://docs.djangoproject.com/en/4.2/topics/email/#console-backend
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# https://docs.djangoproject.com/en/4.2/ref/settings/#default-from-email
# DEFAULT_FROM_EMAIL = f"smtp.{EMAIL_HOST_USER_}"

# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-EMAIL_HOST
# EMAIL_HOST = 'smtp.example.com' # Замените на адрес вашего SMTP-сервера
# EMAIL_HOST = 'mail.privateemail.com'
EMAIL_HOST = "smtp.yandex.ru"
# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-EMAIL_PORT
EMAIL_PORT = 465  # 465
# https://docs.djangoproject.com/en/4.2/ref/settings/#email-host-user
EMAIL_HOST_USER = f"{EMAIL_HOST_USER_}"
# EMAIL_HOST_USER = 'noreply@custom-tools.online'

# https://docs.djangoproject.com/en/4.2/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = f"{EMAIL_HOST_PASSWORD_}"

# https://docs.djangoproject.com/en/4.2/ref/settings/#email-use-ssl
EMAIL_USE_SSL = True  # если порт 465

# https://docs.djangoproject.com/en/4.2/ref/settings/#email-use-tls
# EMAIL_USE_TLS = False
# EMAIL_USE_TLS = True  # если порт 587
# https://docs.djangoproject.com/en/4.2/ref/settings/#email-timeout
EMAIL_TIMEOUT = 60

# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-EMAIL_USE_LOCALTIME
EMAIL_USE_LOCALTIME = True

# https://docs.djangoproject.com/en/4.2/ref/settings/#email-subject-prefix
# EMAIL_SUBJECT_PREFIX = "activation_from_cloud"


# '''Cookie'''
SESSION_COOKIE_HTTPONLY = False  # CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # изменить на True CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"  # CSRF_COOKIE_SAMESITE = 'Lax'  # или 'Strict'
SESSION_COOKIE_AGE = 86400

# '''CSRF'''
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_DOMAIN = ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = [
    "http://80.78.242.36",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://localhost:8000",
]
# CORS
# True, сервер будет принимать запросы из любого источника. Это означает, что
# ваш API будет доступен для всех доменов без ограничений
# Should be False when using specific origins
# Разрешить запросы с любого источника (для разработки)
CORS_ORIGIN_ALLOW_ALL = False
# Или разрешить только определённые домены
CORS_ALLOWED_ORIGINS = [
    "http://80.78.242.36",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:59337",
]
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "Authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# SESSION/CACHES
# https://docs.djangoproject.com/en/4.2/topics/cache/#database-caching

# Database caching
# https://docs.djangoproject.com/en/4.2/topics/cache/#database-caching
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cacher",
        # 'TIMEOUT': 300,
    },
}
# Значение None: Ключи кэша никогда не истекают.
# Значение 0: Ключи истекают немедленно.
# second a live time of session
CACHE_MIDDLEWARE_SECONDS = 300
# HASH
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "accounts.hashers.PBKDF2WrappedMD5PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
            "django.contrib.auth.password_validation.\
UserAttributeSimilarityValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 3,
        },
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
