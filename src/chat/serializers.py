from rest_framework.serializers import ModelSerializer, SerializerMethodField

from chat.models import Message


class MessageSerializer(ModelSerializer):
    """Сериализатор для сообщений."""

    sender_username = SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "sender_username",
            "message",
            "created_at",
            "updated_at",
        )

    def get_sender_username(self, obj: Message) -> str:
        """Получить имя пользователя, отправившего сообщение.

        :param obj: сообщение
        :type obj: Message

        :returns: имя пользователя
        :rtype: str
        """
        return obj.sender.username
