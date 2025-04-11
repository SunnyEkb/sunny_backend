from rest_framework.serializers import ModelSerializer

from api.v1.serializers.fields import FavoriteObjectRelatedField
from api.v1.serializers.users_serializers import UserReadSerializer
from chat.models import Chat


class ChatSerializer(ModelSerializer):
    """Сериализатор для сообщений."""

    subject = FavoriteObjectRelatedField(read_only=True)
    buyer = UserReadSerializer(read_only=True)
    seller = UserReadSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = (
            "id",
            "buyer",
            "seller",
            "subject",
        )
