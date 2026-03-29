from django.contrib import admin

from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Отображение модели уведомлений в админке."""

    list_display = [  # noqa: RUF012
        "text",
        "receiver",
        "created_at",
        "read_at",
    ]
    search_fields = ["text", "receiver_email"]  # noqa: RUF012
    ordering = ["created_at"]  # noqa: RUF012
