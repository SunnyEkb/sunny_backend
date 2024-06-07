from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        group = instance.receiver.get_group_id()
        serializer = NotificationSerializer(instance)
        async_to_sync(channel_layer.group_send)(
            group, {"type": "send_notification", "message": serializer.data}
        )
