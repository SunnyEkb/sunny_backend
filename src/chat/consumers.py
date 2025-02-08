import json

from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.models import Message
from chat.serializers import JSONSerializer
from core.middleware import get_user_from_db


class ChatConsumer(AsyncWebsocketConsumer):
    """Обработчик для подключений к чату."""

    room_group_name = None

    async def connect(self):
        sender_id = self.scope["user"].id
        receiver_id = self.scope["url_route"]["kwargs"]["id"]

        if await get_user_from_db(receiver_id) is None:
            raise DenyConnection("Reciever does not exist")

        self.room_group_name = (
            f"chat_{sender_id}_{receiver_id}"
            if int(sender_id) > int(receiver_id)
            else f"chat_{receiver_id}_{sender_id}"
        )
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()
        messages = await self.get_messages(
            {"room_group_name": self.room_group_name}
        )
        await self.send(text_data=messages)

    async def disconnect(self, close_code):
        if getattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data["message"]

        message = await self.save_message(
            sender=self.scope["user"],
            message=message,
            room_group_name=self.room_group_name,
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message_id": message.id,
            },
        )

    async def chat_message(self, event):
        message = await self.get_messages({"id": event["message_id"]})
        await self.send(text_data=message)

    @database_sync_to_async
    def get_messages(self, filters: dict):
        messages = JSONSerializer().serialize(
            Message.objects.select_related()
            .filter(**filters)
            .select_related("sender")
            .only(
                "sender__id",
                "sender__username",
                "sender__email",
                "sender__last_login",
                "message",
                "created_at",
                "updated_at",
            ),
            fields=(
                "sender__pk",
                "sender__username",
                "sender__email",
                "sender__last_login",
                "message",
                "created_at",
                "updated_at",
            ),
        )
        return messages

    @database_sync_to_async
    def save_message(self, sender, message, room_group_name) -> Message:
        message = Message.objects.create(
            sender=sender, message=message, room_group_name=room_group_name
        )
        return message
