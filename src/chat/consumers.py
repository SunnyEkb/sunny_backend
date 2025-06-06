import json
import logging

from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
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

    async def connect(self):
        """
        Установка соединения.
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

    async def disconnect(self, close_code):
        """
        Отключение соединения. Удаление участника из группы чата.
        """
        try:
            if getattr(self, "room_group_name"):
                await self.channel_layer.group_discard(
                    self.room_group_name, self.channel_name
                )
        except Exception as e:
            logger.exception(e)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Получение сообщения, Сохранение его в БД и отправка его в группу чата.
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

    async def chat_message(self, event):
        """
        Отправка сообщения другим участникам группы чата.
        """

        try:
            await self.send(json.dumps(event["message"], ensure_ascii=False))
        except Exception as e:
            logger.exception(e)

    @database_sync_to_async
    def __get_messages(self, filters: dict) -> ReturnList:
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
    def __save_message(self, sender: AbstractUser, message: str) -> Message:
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

    async def __save_chat_message(
        self, sender: AbstractUser, message: str
    ) -> Message:
        """
        Сохренение нового сообщения в БД и создание чата в БД, если его нет.

        :param sender: отправитель сообщения
        :param message: текст сообщения
        :return: экземпляр сообщения
        """

        if not self.chat:
            self.chat = await self.__create_chat(self.chat_data)

        message = await self.__save_message(sender=sender, message=message)
        return message

    @database_sync_to_async
    def __get_content_type(self, type: str) -> ContentType | None:
        """
        Получение экземплярf ContentType.

        :param type: cтроковое название класса
        :return: экземпляр ContentType
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
    ) -> object | None:
        """
        Получение объекта из БД.

        :param cont_type_model: Экземпляр класса ContentType
        :param cont_type_model: ID объекта
        :return: класс ORM
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
        """
        Создание объекта чата в БД.

        :param data: данные чата
        :return: экземпляр объекта чата
        """

        chat = Chat.objects.create(**data)
        return chat

    @database_sync_to_async
    def __get_chat(self, data: dict) -> Chat | None:
        """
        Получение объекта чата из БД.

        :param data: данные чата
        :return: экземпляр объекта чата
        """

        try:
            chat = Chat.objects.get(**data)
            return chat
        except Chat.DoesNotExist:
            return None
