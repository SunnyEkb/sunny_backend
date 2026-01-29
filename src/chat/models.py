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

    def __str__(self) -> str:
        """Получить строковое представление чата.

        :returns: строковое представление чата
        :rtype: str
        """
        return f"{self.room_group_name}"

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
        constraints = [
            models.CheckConstraint(
                check=~models.Q(seller=models.F("buyer")),
                name="not self chat",
            ),
        ]
        unique_together = [["seller", "buyer", "content_type", "object_id"]]


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
        """Получить строковое представление сообщения.

        :returns: строковое представление сообщения
        :rtype: str
        """
        return f"{self.message}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["created_at"]
