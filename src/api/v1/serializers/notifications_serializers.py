from rest_framework.serializers import ModelSerializer

from notifications.models import Notification


class NotificationSerializer(ModelSerializer):
    """Сериализатор для уведомлений."""

    class Meta:
        model = Notification
        fields = [
            "text",
            "link",
            "created_at",
            "updated_at",
            "read_at",
        ]
