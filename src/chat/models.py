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
    seller = models.ForeignKey(
        User,
        verbose_name="Продавец",
        on_delete=models.PROTECT,
        related_name="chat_as_seller",
        limit_choices_to={"is_active": True},
    )
    buyer = models.ForeignKey(
        User,
        verbose_name="Покупатель",
        on_delete=models.PROTECT,
        related_name="chat_as_buyer",
        limit_choices_to={"is_active": True},
    )

    class Meta:
        """Настройки модели чата."""

        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
        constraints = [  # noqa: RUF012
            models.CheckConstraint(
                check=~models.Q(seller=models.F("buyer")),
                name="not self chat",
            ),
        ]
        unique_together = [  # noqa: RUF012
            ["seller", "buyer", "content_type", "object_id"]
        ]

    def __str__(self) -> str:
        """Получить строковое представление чата.

        Returns:
            str: строковое представление чата

        """
        return f"{self.room_group_name}"


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
    chat = models.ForeignKey(Chat, on_delete=models.PROTECT, related_name="messages")

    class Meta:
        """Настройки модели сообщения."""

        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["created_at"]  # noqa: RUF012

    def __str__(self) -> str:
        """Получить строковое представление сообщения.

        Returns:
            str: строковое представление сообщения

        """
        return f"{self.message}"
