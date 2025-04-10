from rest_framework.serializers import ModelSerializer, SerializerMethodField

from api.v1.serializers.fields import FavoriteObjectRelatedField
from chat.models import Chat


class ChatSerializer(ModelSerializer):
    """Сериализатор для сообщений."""

    subject = FavoriteObjectRelatedField(read_only=True)
    responder_username = SerializerMethodField()
    initiator_username = SerializerMethodField()

    class Meta:
        model = Chat
        fields = (
            "id",
            "responder_username",
            "initiator_username",
            "subject",
        )

    def get_initiator_username(self, obj):
        return obj.initiator.username

    def get_responder_username(self, obj):
        return obj.responder.username
