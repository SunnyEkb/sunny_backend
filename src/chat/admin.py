from django.contrib import admin

from chat.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Класс визуализации сообщений в админке."""

    list_display = [
        "sender",
        "message",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "message",
    ]
    ordering = [
        "chat",
        "created_at",
    ]
