from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.choices import CommentStatus
from core.db_utils import comment_image_path, validate_image
from core.enums import Limits
from core.models import TimeCreateUpdateModel
from comments.managers import CommentManager
from services.tasks import delete_image_files_task, delete_images_dir_task

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
                Limits.MIN_RATING.value,
                f"Оценка не может быть меньше {Limits.MIN_RATING.value}",
            ),
            MaxValueValidator(
                Limits.MAX_RATING.value,
                f"Оценка не может быть больше {Limits.MAX_RATING.value}",
            ),
        ],
    )
    feedback = models.CharField(
        "отзыв", max_length=Limits.MAX_COMMENT_TEXT.value
    )
    status = models.IntegerField(
        "Статус комментария",
        choices=CommentStatus.choices,
        default=CommentStatus.DRAFT.value,
    )

    cstm_mng = CommentManager()
    objects = models.Manager()

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        unique_together = ("author", "content_type", "object_id")

    def __str__(self) -> str:
        return self.feedback[:30]

    def delete_images(self):
        """Удаление фото к комментарию."""

        images = self.images.all()
        if images:
            for image in images:
                image.delete()
            delete_images_dir_task.delay(f"comments/{self.id}")

    def publish(self):
        if self.status == CommentStatus.DRAFT.value:
            self.status = CommentStatus.PUBLISHED.value
            self.save()

    def get_admin_url(self, request) -> str:
        """Возвращает ссылку на экземпляр модели в админке."""

        domain = get_current_site(request).domain
        app_name = self._meta.app_label
        name: str = self.__class__.__name__.lower()
        return "".join(
            ["https://", domain, f"/admin/{app_name}/{name}/{self.id}/change/"]
        )


class CommentImage(models.Model):
    """Фото к комментарию."""

    image = models.ImageField(
        "Фото к комментарию",
        upload_to=comment_image_path,
        validators=[validate_image],
    )
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
        return self.comment.feedback[:30]

    def delete_image_files(self):
        """Удаление файлов изображений."""

        delete_image_files_task.delay(str(self.image))
