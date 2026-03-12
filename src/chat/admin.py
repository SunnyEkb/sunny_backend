from django.contrib import admin

from chat.models import Chat, Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Класс визуализации сообщений в админке."""

    list_display = [  # noqa: RUF012
        "sender",
        "message",
        "created_at",
        "updated_at",
        "chat",
    ]
    search_fields = ["message"]  # noqa: RUF012
    ordering = ["chat", "created_at"]  # noqa: RUF012


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """Класс визуализации чатов в админке."""

    list_display = [  # noqa: RUF012
        "room_group_name",
        "seller",
        "buyer",
    ]
    search_fields = ["room_group_name"]  # noqa: RUF012
    ordering = ["room_group_name"]  # noqa: RUF012
