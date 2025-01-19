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
