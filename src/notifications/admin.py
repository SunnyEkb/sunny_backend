from django.contrib import admin

from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Отображение модели уведомлений в админке.
    """

    list_display = [
        "text",
        "receiver",
        "created_at",
        "read_at",
    ]
    search_fields = ["text", "receiver_email"]
    ordering = ["created_at"]
