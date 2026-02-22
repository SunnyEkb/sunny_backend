from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Настройки приложения 'users'."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self) -> None:
        """импортировать сигналы."""
        import users.signals  # noqa: F401, PLC0415
