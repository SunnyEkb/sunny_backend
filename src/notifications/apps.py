from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Настройки приложения 'notifications'."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"

    def ready(self) -> None:
        """Запуск приложения."""
        import notifications.signals  # noqa: F401, PLC0415
