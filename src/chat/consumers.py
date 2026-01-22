import json
import logging
from typing import Any

from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Model
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from rest_framework.utils.serializer_helpers import ReturnList

from chat.models import Chat, Message
from chat.serializers import MessageSerializer
from core.middleware import get_user_from_db
from core.choices import AdvertisementStatus

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """Обработчик для подключений к чату."""

    room_group_name = None
    chat_data = None
    chat = None

    async def connect(self) -> None:
        """Установка соединения.

        Создание группы чата и отправка в нее сообщений чата.
        """
        try:
            sender_id = self.scope["user"].id
            object_id = self.scope["url_route"]["kwargs"]["object_id"]
            type = self.scope["url_route"]["kwargs"]["type"]
            buyer_id = self.scope["url_route"]["kwargs"]["buyer_id"]

            cont_type_model = await self.__get_content_type(type)
            if cont_type_model is None:
                raise DenyConnection("Content type not found!")

            obj = await self.__get_object(cont_type_model, object_id)
            if obj is None:
                raise DenyConnection("Object not found.")

            if obj.status != AdvertisementStatus.PUBLISHED:
                raise DenyConnection("Object not published.")

            buyer = await get_user_from_db(buyer_id)
            seller = obj.provider
            sender = await get_user_from_db(sender_id)

            self.room_group_name = f"chat_{type}_{object_id}_{buyer_id}"
            self.chat_data = {
                "room_group_name": self.room_group_name,
                "content_type": cont_type_model,
                "object_id": object_id,
                "buyer": buyer,
                "seller": seller,
            }

            if sender == seller:
                chat = await self.__get_chat(self.chat_data)
                if chat is None:
                    raise DenyConnection("Do not write to yourself")
                await self.channel_layer.group_add(
                    self.room_group_name, self.channel_name
                )
                await self.accept()
                self.chat = chat
                messages = await self.__get_messages({"chat": self.chat})
                await self.send(json.dumps(messages, ensure_ascii=False))

            elif sender == buyer:
                await self.channel_layer.group_add(
                    self.room_group_name, self.channel_name
                )
                await self.accept()
                chat = await self.__get_chat(self.chat_data)
                if chat is not None:
                    self.chat = chat
                    messages = await self.__get_messages({"chat": self.chat})
                    await self.send(json.dumps(messages, ensure_ascii=False))
            else:
                raise DenyConnection("Access Denied: Forbidden!")
        except DenyConnection:
            raise
        except Exception as e:
            logger.exception(e)

    async def disconnect(self, close_code: Any) -> None:
        """Отключить соединение.

        Удаляет участника из группы чата.

        :param close_code: код закрытия
        :type close_code: Any
        """
        try:
            if getattr(self, "room_group_name"):
                await self.channel_layer.group_discard(
                    self.room_group_name, self.channel_name
                )
        except Exception as e:
            logger.exception(e)

    async def receive(
        self, text_data: str, bytes_data: bytes | None = None
    ) -> None:
        """Получить сообщения.

        Сохраняет сообщение в БД и отправляет его в группу чата.

        :param text_data: Данные в текстовом формате
        :type text_data: str
        :param bytes_data: Данные в байтах
        :type bytes_data: bytes | None
        """
        try:
            data = json.loads(text_data)
            message = data.get("message", None)

            if message and isinstance(message, str):
                message = await self.__save_chat_message(
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
        except Exception as e:
            logger.exception(e)

    async def chat_message(self, event: Any) -> None:
        """Отправить сообщения другим участникам группы чата.

        :param event: Событие
        :type event: Any
        """
        try:
            await self.send(json.dumps(event["message"], ensure_ascii=False))
        except Exception as e:
            logger.exception(e)

    @database_sync_to_async
    def __get_messages(self, filters: dict) -> ReturnList:
        """Получить список сообщений из БД.

        :param filters: параметры фильтрации
        :type filters: dict

        :returns: экземпляр сообщения, если найден, или None
        :rtype: ReturnList
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
    def __save_message(self, sender: AbstractUser, message: str) -> Message:
        """Сохранить новое сообщение в БД.

        :param sender: отправитель сообщения
        :type sender: AbstractUser
        :param message: текст сообщения
        :type message: str

        :returns: экземпляр сообщения
        :rtype: Message
        """
        msg = Message.objects.create(
            sender=sender, message=message, chat=self.chat
        )
        return msg

    async def __save_chat_message(
        self, sender: AbstractUser, message: str
    ) -> Message:
        """Сохранить сообщение в БД.

        Если чат не существует, создается новый.

        :param sender: отправитель сообщения
        :type sender: AbstractUser
        :param message: текст сообщения
        :type message: str

        :returns: экземпляр сообщения
        :rtype: Message
        """
        if not self.chat:
            self.chat = await self.__create_chat(self.chat_data)

        msg = await self.__save_message(sender=sender, message=message)
        return msg

    @database_sync_to_async
    def __get_content_type(self, type: str) -> ContentType | None:
        """Получить экземпляр ContentType.

        :param type: cтроковое название класса
        :type type: str

        :returns: экземпляр ContentType если найден
        :rtype: ContentType | None
        """
        try:
            return ContentType.objects.get(
                app_label=f"{type}s", model=f"{type}"
            )
        except ContentType.DoesNotExist:
            return None

    @database_sync_to_async
    def __get_object(
        self, cont_type_model: ContentType, object_id: int
    ) -> Model | None:
        """Получить объект из БД.

        :param cont_type_model: Экземпляр класса ContentType
        :type cont_type_model: ContentType
        :param object_id: ID объекта
        :type object_id: int

        :returns: класс ORM
        :rtype: Model | None
        """
        try:
            return (
                cont_type_model.model_class()
                .objects.select_related("provider")
                .get(pk=object_id)
            )
        except cont_type_model.model_class().DoesNotExist:
            return None

    @database_sync_to_async
    def __create_chat(self, data: dict) -> Chat:
        """Создать объект чата в БД.

        :param data: данные чата
        :type data: dict

        :returns: экземпляр объекта чата
        :rtype: Chat
        """
        chat = Chat.objects.create(**data)
        return chat

    @database_sync_to_async
    def __get_chat(self, data: dict) -> Chat | None:
        """Получить объект чата из БД.

        :param data: данные чата
        :type data: dict

        :return: экземпляр объекта чата, есди найден
        :rtype: Chat | None
        """
        try:
            chat = Chat.objects.get(**data)
            return chat
        except Chat.DoesNotExist:
            return None
