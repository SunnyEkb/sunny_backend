import json

from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType

from chat.models import Chat, Message
from chat.serializers import MessageSerializer
from core.middleware import get_user_from_db
from core.choices import AdvertisementStatus


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
        object_id = self.scope["url_route"]["kwargs"]["object_id"]
        type = self.scope["url_route"]["kwargs"]["type"]
        buyer_id = self.scope["url_route"]["kwargs"]["buyer_id"]

        cont_type_model = await self.get_content_type(type)
        if cont_type_model is None:
            raise DenyConnection("Wrong object type.")

        obj = await self.get_object(cont_type_model, object_id)
        if obj is None:
            raise DenyConnection("Object not found.")

        if obj.status != AdvertisementStatus.PUBLISHED:
            raise DenyConnection("Object not published.")

        initiator = await get_user_from_db(buyer_id)
        responder = obj.provider
        sender = await get_user_from_db(sender_id)

        self.room_group_name = (
            f"chat_{type}_{object_id}_{buyer_id}"
        )
        chat_data = {
            "room_group_name": self.room_group_name,
            "content_type": cont_type_model,
            "object_id": object_id,
            "initiator": initiator,
            "responder": responder,
        }

        if sender == responder:
            chat = await self.get_chat(chat_data)
            if chat is None:
                raise DenyConnection("Do not write to yourself")
            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )
            await self.accept()
            self.chat = chat

        elif sender == initiator:
            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )
            await self.accept()
            self.chat, _ = await self.get_or_create_chat(chat_data)
        else:
            raise DenyConnection("Access Denied: Forbidden!")

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

        return ContentType.objects.get(app_label=f"{type}s", model=f"{type}")

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
            .objects.select_related("provider")
            .get(pk=object_id)
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

    @database_sync_to_async
    def create_chat(self, data: dict) -> Chat:
        """
        Создание объекта чата в БД.

        :param data: данные чата
        :return: экземпляр объекта чата
        """

        chat = Chat.objects.create(**data)
        return chat

    @database_sync_to_async
    def get_chat(self, data: dict) -> Chat | None:
        """
        Получение объекта чата из БД.

        :param data: данные чата
        :return: экземпляр объекта чата
        """

        chat = Chat.objects.get(**data)
        return chat
