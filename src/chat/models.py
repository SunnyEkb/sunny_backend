from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.abstract_models import TimeCreateUpdateModel

User = get_user_model()


class Chat(models.Model):
    """Чат."""

    room_group_name = models.CharField(unique=True, max_length=100)
    limit = models.Q(app_label="services", model="service") | models.Q(
        app_label="ads", model="ad"
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Тип объекта чата",
        limit_choices_to=limit,
    )
    object_id = models.PositiveIntegerField("ID объекта")
    subject = GenericForeignKey("content_type", "object_id")
    responder = models.ForeignKey(
        User,
        verbose_name="Ответчик",
        on_delete=models.PROTECT,
        related_name="chat_responder",
        limit_choices_to={"is_active": True},
    )
    initiator = models.ForeignKey(
        User,
        verbose_name="Инициатор",
        on_delete=models.PROTECT,
        related_name="chat_initiator",
        limit_choices_to={"is_active": True},
    )

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
        constraints = [
            models.CheckConstraint(
                check=~models.Q(responder=models.F("initiator")),
                name="not self chat",
            ),
        ]
        unique_together = [
            ["responder", "initiator", "content_type", "object_id"]
        ]


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
