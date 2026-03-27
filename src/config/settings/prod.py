from config.settings.base import *  # noqa: F403

DEBUG = False

CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

SIMPLE_JWT["AUTH_COOKIE_SAMESITE"] = "Lax"  # noqa: F405
