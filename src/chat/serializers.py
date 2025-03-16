from rest_framework.serializers import ModelSerializer, SerializerMethodField

from chat.models import Message


class MessageSerializer(ModelSerializer):
    """Сериализатор сообщения чата."""

    sender_username = SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "sender_username",
            "message",
            "room_group_name",
            "created_at",
            "updated_at",
        )

    def get_sender_username(self, obj):
        return obj.sender.username
