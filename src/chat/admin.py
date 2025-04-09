from django.contrib import admin

from chat.models import Chat, Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Класс визуализации сообщений в админке."""

    list_display = [
        "sender",
        "message",
        "created_at",
        "updated_at",
    ]
    search_fields = ["message"]
    ordering = ["chat", "created_at"]


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """Класс визуализации чатов в админке."""

    list_display = [
        "room_group_name",
        "responder",
        "initiator",
    ]
    search_fields = ["room_group_name"]
    ordering = ["room_group_name"]
