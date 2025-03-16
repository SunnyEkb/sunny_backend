from django.contrib import admin

from chat.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Класс визуализации сообщений в админке."""

    list_display = [
        "sender",
        "message",
        "room_group_name",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "message",
        "room_group_name",
    ]
    ordering = ["created_at", "room_group_name"]
