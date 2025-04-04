from django.contrib.auth import get_user_model
from django.db import models

from core.abstract_models import TimeCreateUpdateModel

User = get_user_model()


class Chat(models.Model):
    """Чат."""

    room_group_name = models.CharField(unique=True, max_length=100)
    members = models.ManyToManyField(
        User,
        verbose_name="Участники",
        through="ChatMembers",
        through_fields=("chat", "initiator"),
    )

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"


class Message(TimeCreateUpdateModel):
    """Cообщениe."""

    sender = models.ForeignKey(
        User,
        verbose_name="Отправитель",
        on_delete=models.CASCADE,
        related_name="messages",
        limit_choices_to={"is_active": True},
    )
    message = models.TextField(null=False, blank=False)
    chat = models.ForeignKey(
        Chat, on_delete=models.PROTECT, related_name="messages"
    )

    def __str__(self) -> str:
        return f"{self.message}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["-created_at"]


class ChatMembers(models.Model):
    """Участники чата."""

    chat = models.ForeignKey(Chat, on_delete=models.PROTECT)
    responder = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="chat_responder",
        limit_choices_to={"is_active": True},
    )
    initiator = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="chat_initiator",
        limit_choices_to={"is_active": True},
    )

    class Meta:
        verbose_name = "Участники чата"
        verbose_name_plural = "Участники чатов"
        unique_together = [["chat", "responder", "initiator"]]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(first=models.F("second")),
                name="not self chat",
            ),
        ]
