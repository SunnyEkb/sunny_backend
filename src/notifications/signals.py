from typing import Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.v1.serializers import NotificationSerializer
from notifications.models import Notification


@receiver(post_save, sender=Notification)
def send_notification(
    sender: Any,  # noqa: ANN401, ARG001
    instance: Notification,
    created: bool,  # noqa: FBT001
    **kwargs  # noqa: ANN003, ARG001
) -> None:
    """Отправить уведомление.

    Args:
        sender (Any): класс модели
        instance (Notification): экземпляр класса
        created (bool): отметка о создании экземпляра класса
        **kwargs (dict): дополнительные именованные аргументы

    """
    if created:
        channel_layer = get_channel_layer()
        group = instance.receiver.get_group_id()
        serializer = NotificationSerializer(instance)
        async_to_sync(channel_layer.group_send)(
            group, {"type": "send_notification", "message": serializer.data}
        )
