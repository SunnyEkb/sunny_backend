from rest_framework.serializers import ModelSerializer

from api.v1.serializers.fields import FavoriteObjectRelatedField
from chat.models import Chat


class ChatSerializer(ModelSerializer):
    """Сериализатор для сообщений."""

    subject = FavoriteObjectRelatedField(read_only=True)

    class Meta:
        model = Chat
        fields = (
            "id",
            "responder",
            "initiator",
            "subject",
        )

    def get_initiator_username(self, obj):
        return obj.initiator.username

    def get_responder_username(self, obj):
        return obj.responder.username
