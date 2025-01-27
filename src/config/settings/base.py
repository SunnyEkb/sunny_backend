from datetime import timedelta
from os import getenv
from pathlib import Path

from corsheaders.defaults import default_headers
from django.core.files.storage import FileSystemStorage
from dotenv import load_dotenv

TRUE_VALUES = ["1", "true", "True", "YES", "yes"]
BASE_DIR = Path(__file__).resolve().parent.parent.parent

dotenv_path = Path(BASE_DIR, "../.env")
load_dotenv(dotenv_path)

SECRET_KEY = getenv("SECRET_KEY", default="secret_key")

DEBUG = True if getenv("DEBUG") in TRUE_VALUES else False

ALLOWED_HOSTS = getenv("ALLOWED_HOSTS", default="").split(", ")

DOMAIN = getenv("DOMAIN", default="127.0.0.1")
APPEND_SLASH = False

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "django_rest_passwordreset",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "oauth2_provider",
    "social_django",
    "drf_social_oauth2",
    "corsheaders",
    "users",
    "notifications",
    "services",
    "ads",
    "comments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "core.middleware.CsrfHeaderMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES_DIR = Path(BASE_DIR, "templates")
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

ASGI_APPLICATION = "config.asgi.application"
# WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": getenv("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": getenv("POSTGRES_DB", default="db_test"),
        "USER": getenv("POSTGRES_USER", default="admin_test"),
        "PASSWORD": getenv("POSTGRES_PASSWORD", default="postgre_admin"),
        "HOST": getenv("POSTGRES_HOST", default="db_test"),
        "PORT": getenv("POSTGRES_PORT", default=5432),
    }
}

AUTH_USER_MODEL = "users.CustomUser"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation"
            ".UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),
    },
]

AUTHENTICATION_BACKENDS = (
    "drf_social_oauth2.backends.DjangoOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "api.v1.auth.CustomAuthentication",
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        "drf_social_oauth2.authentication.SocialAuthentication",
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "10000/day",
        "anon": "1000/day",
    },
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(getenv("ACCESS_TOKEN_LIFETIME", default=5))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(getenv("REFRESH_TOKEN_LIFETIME", default=14))
    ),
    "AUTH_COOKIE": getenv("AUTH_COOKIE", default="access"),
    "AUTH_REFRESH": getenv("AUTH_REFRESH", default="refresh"),
    "AUTH_COOKIE_DOMAIN": None,
    "AUTH_COOKIE_SECURE": True,
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_PATH": "/",
    "AUTH_COOKIE_SAMESITE": "None",  # "Lax" заменить на проде
}

DRFSO2_PROPRIETARY_BACKEND_NAME = "VK.com"
DRFSO2_URL_NAMESPACE = "social_auth"
ACTIVATE_JWT = True

SOCIAL_AUTH_VK_OAUTH2_KEY = getenv("SOCIAL_AUTH_VK_OAUTH2_KEY")
SOCIAL_AUTH_VK_OAUTH2_SECRET = getenv("SOCIAL_AUTH_VK_OAUTH2_SECRET")

CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CORS_EXPOSE_HEADERS = ["Content-Type", "X-CSRFToken"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SAMESITE = "None"
CSRF_TRUSTED_ORIGINS = getenv(
    "CSRF_TRUSTED_ORIGINS", default="http://127.0.0.1"
).split(", ")
CORS_ALLOWED_ORIGINS = getenv(
    "CORS_ALLOWED_ORIGINS", default="http://127.0.0.1"
).split(", ")
CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

CORS_ALLOW_HEADERS = (
    *default_headers,
    "X-CSRFToken",
)

SPECTACULAR_SETTINGS = {
    "TITLE": "Sunny Ekb Documentation",
    "DESCRIPTION": "Documentation for Sunny Ekb API built with DRF",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "filter": True,
    },
}

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = Path(BASE_DIR, "static")
MEDIA_URL = "media/"
MEDIA_ROOT = Path(BASE_DIR, "media")
PATH_TO_SAVE_DELETED_USERS_DATA = FileSystemStorage(
    location=Path(BASE_DIR, "data_store")
)
DATA_RETENTION_PERIOD = timedelta(weeks=53 * 5)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True if getenv("EMAIL_USE_TLS") == "YES" else False
EMAIL_USE_SSL = False
EMAIL_PORT = getenv("EMAIL_PORT")
EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_HOST_PASSWORD = getenv("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = getenv("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = getenv("EMAIL_HOST_USER")
SERVER_EMAIL = getenv("EMAIL_HOST_USER")

TELEGRAM_SUPPORT_CHAT_ID = getenv("TELEGRAM_SUPPORT_CHAT_ID")
TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")
TELEGRAM_MODERATORS_CHAT_ID = getenv("TELEGRAM_MODERATORS_CHAT_ID", "").split(
    ", "
)
TELEGRAM_MODERATORS_CHAT_TOPIC = getenv("TELEGRAM_MODERATORS_CHAT_TOPIC", "")

REDIS_HOST = getenv("REDDIS_HOST", default="127.0.0.1")
REDIS_PORT = getenv("REDDIS_PORT", default=6379)
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600}
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

ERROR_LOG_FILENAME = Path(BASE_DIR, getenv("ERROR_LOG_FILENAME", "errors.log"))
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "main": {
            "format": "%(asctime)s, %(name)s, %(levelname)s, %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(asctime)s, %(message)s",
        },
    },
    "handlers": {
        "file_logger": {
            "formatter": "main",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": (
                ERROR_LOG_FILENAME
                if Path(ERROR_LOG_FILENAME).exists()
                else "errors.log"
            ),
        },
        "console_logger": {
            "formatter": "simple",
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "telegram_logger": {
            "formatter": "main",
            "()": "core.log.TelegramHandler",
            "level": "ERROR",
        },
    },
    "loggers": {
        "django.server": {
            "level": "INFO",
            "handlers": ["console_logger"],
            "propagate": True,
        },
        "django": {
            "level": "ERROR",
            "handlers": ["file_logger", "telegram_logger"],
            "propagate": False,
        },
        "factory": {
            "level": "WARN",
        },
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}
