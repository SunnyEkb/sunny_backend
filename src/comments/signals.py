from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from comments.models import Comment


@receiver(post_save, sender=Comment)
def notify_about_comment_creation(
    sender: Any, instance: Comment, created: bool, **kwargs
) -> None:
    """Уведомить о создании комментария."""

    if created:
        instance.notify_about_comment_creation()
