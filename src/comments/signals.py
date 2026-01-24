from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from comments.models import Comment


@receiver(post_save, sender=Comment)
def notify_about_comment_creation(
    sender: Any, instance: Comment, created: bool, **kwargs
) -> None:
    """Уведомить о создании комментария.

    :param sender: класс модели
    :type sender: Any
    :param instance: экземпляр класса
    :type instance: Comment
    :param created: отметка о создании экземпляра класса
    :type created: bool
    """
    if created:
        instance.notify_about_comment_creation()
