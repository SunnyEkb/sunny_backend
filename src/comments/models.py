import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.abstract_models import AbstractImage, TimeCreateUpdateModel
from core.choices import CommentStatus
from core.enums import Limits
from comments.managers import CommentManager
from services.tasks import delete_images_dir_task, notify_about_moderation_task

User = get_user_model()


class Comment(TimeCreateUpdateModel):
    """Комментарий."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор"
    )
    limit = models.Q(app_label="services", model="service") | models.Q(
        app_label="ads", model="ad"
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="К чему комментарий",
        limit_choices_to=limit,
    )
    object_id = models.PositiveIntegerField("ID объекта")
    subject = GenericForeignKey("content_type", "object_id")
    rating = models.PositiveIntegerField(
        "Оценка",
        validators=[
            MinValueValidator(
                Limits.MIN_RATING,
                f"Оценка не может быть меньше {Limits.MIN_RATING}",
            ),
            MaxValueValidator(
                Limits.MAX_RATING,
                f"Оценка не может быть больше {Limits.MAX_RATING}",
            ),
        ],
    )
    feedback = models.CharField("отзыв", max_length=Limits.MAX_COMMENT_TEXT)
    status = models.IntegerField(
        "Статус комментария",
        choices=CommentStatus.choices,
        default=CommentStatus.MODERATION,
    )

    cstm_mng = CommentManager()
    objects = models.Manager()

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        unique_together = ("author", "content_type", "object_id")

    def __str__(self) -> str:
        """Получить строковое представление комментария.

        :returns: строковое представление комментария
        :rtype: str
        """
        return self.feedback[:30]

    def delete_images(self) -> None:
        """Создать задачу по удалению фото к комментарию."""
        images = self.images.all()
        if images:
            for image in images:
                image.delete()
            delete_images_dir_task.delay(f"comments/{self.id}")

    def approve(self) -> None:
        """Утвердить комментарий.

        Статус комментария меняется на 'PUBLISHED'.
        """
        if self.status == CommentStatus.MODERATION:
            self.status = CommentStatus.PUBLISHED
            self.save()

    def reject(self) -> None:
        """Отклонить комментарий.

        Создается задача по удалению фото к комментарию. \
        Сам комменарий удаляется.
        """
        if self.status == CommentStatus.MODERATION:
            self.delete_images()
            self.delete()

    def notify_about_comment_creation(self) -> None:
        """Создать уведомление о создании комментария.

        Создает задачу о необходимости модерации комментария.
        """
        url = self.get_admin_url()
        if "test" not in sys.argv:
            notify_about_moderation_task.delay(url)

    def get_admin_url(self) -> str:
        """Возвращает ссылку на экземпляр модели в админке.

        :returns: ссылка на экземпляр модели в админке
        :rtype: str
        """
        app_name = self._meta.app_label
        name: str = self.__class__.__name__.lower()
        return "".join(
            [
                "https://",
                settings.DOMAIN,
                f"/admin/{app_name}/{name}/{self.id}/change/",
            ]
        )


class CommentImage(AbstractImage):
    """Фото к комментарию."""

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        verbose_name="Комментарий",
        related_name="images",
    )

    class Meta:
        verbose_name = "Фото к комментарию"
        verbose_name_plural = "Фото к комментариям"

    def __str__(self) -> str:
        """Получить строковое представление фото к комментарию.

        :returns: строковое представление фото к комментарию
        :rtype: str
        """
        return self.comment.feedback[:30]
