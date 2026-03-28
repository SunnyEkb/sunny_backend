from .base import *  # noqa: F403

DEBUG = getenv("DEBUG", default="True") == "True"  # noqa: F405

if getenv("USE_SQLITE", default="False") == "True":  # noqa: F405
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "sunny.sqlite3"),  # noqa: F405
        }
    }

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGGING["handlers"].pop("telegram_logger", None)  # type: ignore  # noqa: F405, PGH003
LOGGING["loggers"]["django"]["handlers"] = ["file_logger"]  # type: ignore  # noqa: F405, PGH003

LOGGING["loggers"].update(  # type: ignore  # noqa: F405, PGH003
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
    getenv("CELERY_TASK_ALWAYS_EAGER", default="False") == "True"  # noqa: F405
)
CELERY_BROKER_URL = getenv("CELERY_BROKER_URL", default="")  # noqa: F405
CELERY_RESULT_BACKEND = getenv("CELERY_RESULT_BACKEND", default="cache")  # noqa: F405
CELERY_CACHE_BACKEND = getenv("CELERY_CACHE_BACKEND", default="memory")  # noqa: F405

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

ELASTICSEARCH_DSL_SIGNAL_PROCESSOR = (
    "django_elasticsearch_dsl.signals.RealTimeSignalProcessor"
)

INSTALLED_APPS.remove("django_elasticsearch_dsl")  # noqa: F405
