from .base import *  # noqa

DEBUG = getenv("DEBUG", default="True") == "True"  # noqa

if getenv("USE_SQLITE", default="False") == "True":  # noqa
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "sunny.sqlite3"),  # noqa
        }
    }

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGGING["handlers"].pop("telegram_logger", None)  # type: ignore  # noqa
LOGGING["loggers"]["django"]["handlers"] = ["file_logger"]  # type: ignore  # noqa

LOGGING["loggers"].update(  # type: ignore  # noqa
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
    if (getenv("CELERY_TASK_ALWAYS_EAGER", default="False") == "True")  # noqa
    else False
)
CELERY_BROKER_URL = getenv("CELERY_BROKER_URL", default="")  # noqa
CELERY_RESULT_BACKEND = getenv("CELERY_RESULT_BACKEND", default="cache")  # noqa
CELERY_CACHE_BACKEND = getenv("CELERY_CACHE_BACKEND", default="memory")  # noqa

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

ELASTICSEARCH_DSL_SIGNAL_PROCESSOR = (
    "django_elasticsearch_dsl.signals.RealTimeSignalProcessor"
)

INSTALLED_APPS.remove("django_elasticsearch_dsl")  # noqa
