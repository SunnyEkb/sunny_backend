import json

from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType

from chat.models import Chat, Message
from chat.serializers import MessageSerializer
from core.middleware import get_user_from_db


class ChatConsumer(AsyncWebsocketConsumer):
    """Обработчик для подключений к чату."""

    room_group_name = None
    chat_id = None

    async def connect(self):
        """
        Установка соединения.
        Создание группы чата и отправка в нее сообщений чата.
        """

        sender_id = self.scope["user"].id
        receiver_id = self.scope["url_route"]["kwargs"]["reciever_id"]
        object_id = self.scope["url_route"]["kwargs"]["object_id"]
        type = self.scope["url_route"]["kwargs"]["type"]

        cont_type_model = await self.get_content_type(type)
        if cont_type_model is None:
            raise DenyConnection("Wrong object type.")

        obj = await self.get_object(cont_type_model, object_id)
        if obj is None:
            raise DenyConnection("Object not found.")

        if await get_user_from_db(receiver_id) is None:
            raise DenyConnection("Reciever does not exist.")

        initiator = get_user_from_db(sender_id)
        responder = obj.provider

        if sender_id == obj.provider:
            raise DenyConnection("Do not write to yourself.")

        if receiver_id != responder:
            raise DenyConnection("Wrong user.")

        self.room_group_name = (
            f"chat_{type}_{object_id}_{sender_id}_{receiver_id}"
        )
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

        chat_data = {
            "room_group_name": self.room_group_name,
            "content_type": cont_type_model,
            "object_id": object_id,
            "initiator": initiator,
            "responder": responder,
        }
        self.chat, _ = await self.get_or_create_chat(chat_data)
        messages = await self.get_messages({"chat": self.chat})
        await self.send(json.dumps(messages, ensure_ascii=False))

    async def disconnect(self, close_code):
        """
        Отключение соединения. Удаление участника из группы чата.
        """

        if getattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Получение сообщения, Сохранение его в БД и отправка его в группу чата.
        """

        data = json.loads(text_data)
        message = data["message"]

        message = await self.save_message(
            sender=self.scope["user"],
            message=message,
            chat=self.chat,
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": MessageSerializer(message).data,
            },
        )

    async def chat_message(self, event):
        """
        Отправка сообщения другим участникам группы чата.
        """

        await self.send(json.dumps(event["message"], ensure_ascii=False))

    @database_sync_to_async
    def get_messages(self, filters: dict) -> Message | None:
        """
        Получение списка сообщений из БД.

        :param filters: параметры фильтрации
        :return: экземпляр сообщения, если найден, или None
        """

        messages = MessageSerializer(
            Message.objects.filter(**filters)
            .select_related("sender")
            .only(
                "id",
                "sender__username",
                "message",
                "created_at",
                "updated_at",
            ),
            many=True,
        ).data
        return messages

    @database_sync_to_async
    def save_message(self, sender: AbstractUser, message: str) -> Message:
        """
        Сохренение нового сообщения в БД.

        :param sender: отправитель сообщения
        :param message: текст сообщения
        :return: экземпляр сообщения
        """

        message = Message.objects.create(
            sender=sender, message=message, chat=self.chat
        )
        return message

    @database_sync_to_async
    def get_content_type(self, type: str) -> ContentType | None:
        """
        Получение экземплярf ContentType.

        :param type: cтроковое название класса
        :return: экземпляр ContentType
        """

        return ContentType.get(app_label=f"{type}s", model=f"{type}")

    @database_sync_to_async
    def get_object(
        self, cont_type_model: ContentType, object_id: int
    ) -> object | None:
        """
        Получение объекта из БД.

        :param cont_type_model: Экземпляр класса ContentType
        :param cont_type_model: ID объекта
        :return: класс ORM
        """

        return (
            cont_type_model.model_class()
            .get(pk=object_id)
            .select_related("provider")
        )

    @database_sync_to_async
    def get_or_create_chat(self, data: dict) -> Chat:
        """
        Создание или получение объекта чата из БД.

        :param data: данные чата
        :return: экземпляр объекта чата
        """

        chat = Chat.objects.get_or_create(**data)
        return chat
