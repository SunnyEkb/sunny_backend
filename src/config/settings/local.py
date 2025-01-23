from .base import *  # noqa

DEBUG = getenv("DEBUG", default="True") == "True"

if getenv("USE_SQLITE", default="False") == "True":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
        }
    }

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGGING["handlers"].pop("telegram_logger", None)
LOGGING["loggers"]["django"]["handlers"] = ["file_logger"]

LOGGING["loggers"].update(
    {
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": [
                "console_logger",
            ],
            "propagate": False,
        }
    }
)

CELERY_TASK_ALWAYS_EAGER = (
    True
    if (getenv("CELERY_TASK_ALWAYS_EAGER", default="False") == "True")
    else False
)
CELERY_BROKER_URL = getenv("CELERY_BROKER_URL", default=None)
CELERY_RESULT_BACKEND = getenv("CELERY_RESULT_BACKEND", default="cache")
CELERY_CACHE_BACKEND = getenv("CELERY_CACHE_BACKEND", default="memory")

CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
}
