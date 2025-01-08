from django.contrib.auth import get_user_model
from django.db import models

from core.db_utils import get_path_to_save_image, validate_image
from services.tasks import delete_image_files_task

User = get_user_model()


class TimeCreateModel(models.Model):
    """Абстрактная модель с полем "Время создания"."""

    created_at = models.DateTimeField(
        "Время создания",
        auto_now_add=True,
        null=True,
        db_index=True,
    )

    class Meta:
        abstract = True


class TimeCreateUpdateModel(TimeCreateModel):
    """
    Абстрактная модель с полями "Время создания" и "Время изменения".
    """

    updated_at = models.DateTimeField("Время изменения", auto_now=True)

    class Meta:
        abstract = True


class AbstractImage(models.Model):
    """Абстрактная модель Изображений."""

    image = models.ImageField(
        "Фото",
        upload_to=get_path_to_save_image,
        validators=[validate_image],
    )

    class Meta:
        abstract = True

    def delete_image_files(self):
        """Удаление файлов изображений."""

        delete_image_files_task.delay(str(self.image))
