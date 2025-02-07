from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from core.abstract_models import TimeCreateUpdateModel
from core.enums import Limits

User = get_user_model()


class Notification(TimeCreateUpdateModel):
    """Уведомление."""

    text = models.TextField(
        "Текст уведомления",
        max_length=Limits.MAX_LENGTH_NOTIFICATION_TEXT.value,
    )
    link = models.URLField(
        "Ссылка на ресурс",
        blank=True,
        null=True,
    )
    sender = models.ForeignKey(
        User,
        verbose_name="Отправитель уведомления",
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_notifications",
    )
    receiver = models.ForeignKey(
        User,
        verbose_name="Получатель уведомления",
        related_name="received_notifications",
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
    )
    read_at = models.DateTimeField(
        "Время прочтения",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ["receiver", "-created_at"]

    def __str__(self):
        return self.text[:30]

    def mark_as_read(self):
        if self.unread():
            self.read_at = timezone.now()
            self.save()

    def mark_as_unread(self):
        if self.read():
            self.read_at = None
            self.save()

    def read(self):
        return bool(self.read_at)

    def unread(self):
        return bool(not self.read_at)
