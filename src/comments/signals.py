from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from comments.models import Comment


@receiver(post_save, sender=Comment)
def notify_about_comment_creation(
    sender: Any,  # noqa: ANN401, ARG001
    instance: Comment,
    created: bool,  # noqa: FBT001
    **kwargs  # noqa: ANN003, ARG001
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
