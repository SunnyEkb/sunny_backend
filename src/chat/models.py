from django.contrib.auth import get_user_model
from django.db import models

from core.abstract_models import TimeCreateUpdateModel

User = get_user_model()


class Message(TimeCreateUpdateModel):
    """Модель сообщения."""

    sender = models.ForeignKey(
        User,
        verbose_name="Отправитель",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="messages",
    )
    message = models.TextField(null=False, blank=False)
    room_group_name = models.CharField(null=False, blank=False, max_length=100)

    def __str__(self) -> str:
        return (
            f"{self.sender.username}-{self.room_group_name}"
            if self.sender
            else f"{self.message}-{self.room_group_name}"
        )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = [
            "-created_at",
        ]
