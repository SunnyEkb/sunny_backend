from django.db import models
from django.core.validators import MaxValueValidator

from core.choices import ServiceCategory, ServicePlace
from core.db_utils import service_image_path, validate_image
from core.enums import Limits
from core.models import AbstractAdvertisement
from services.managers import ServiceManager
from services.tasks import delete_image_files, delete_service_images_dir


class Type(models.Model):
    """Тип услуги."""

    title = models.CharField(
        "Название",
        max_length=Limits.MAX_LENGTH_TYPE_TITLE.value,
    )

    category = models.CharField(
        "Вид услуги",
        max_length=Limits.MAX_LENGTH_ADVMNT_CATEGORY.value,
        choices=ServiceCategory,
    )

    class Meta:
        verbose_name = "Тип услуги"
        verbose_name_plural = "Типы услуг"
        index_together = ["category", "title"]
        ordering = ["category", "title"]

    def __str__(self) -> str:
        return self.title


class Service(AbstractAdvertisement):
    """Услуга."""

    experience = models.PositiveIntegerField(
        "Опыт",
        default=0,
        validators=[MaxValueValidator(Limits.MAXIMUM_EXPERIENCE.value)],
    )
    place_of_provision = models.CharField(
        "Место оказания услуги",
        max_length=Limits.MAX_LENGTH_SERVICE_PLACE.value,
        choices=ServicePlace.choices,
        default=ServicePlace.OPTIONS.value,
    )
    type = models.ForeignKey(
        Type,
        on_delete=models.PROTECT,
        verbose_name="Тип услуги",
        null=True,
    )
    price = models.JSONField("Прайс", blank=True, null=True)

    objects = models.Manager()
    cstm_mng = ServiceManager()

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = [
            "-created_at",
        ]

    def __str__(self) -> str:
        return self.title

    def delete_service_images(self):
        """Удаление фото к услуге."""

        images = self.images.all()
        if images:
            for image in images:
                image.delete()
            delete_service_images_dir.delay(f"services/{self.id}")


class ServiceImage(models.Model):
    """Фото к услуге."""

    image = models.ImageField(
        "Фото к услуге",
        upload_to=service_image_path,
        validators=[validate_image],
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name="Услуга",
        related_name="images",
    )
    main_photo = models.BooleanField(
        "Основное фото",
        default=False,
    )

    class Meta:
        verbose_name = "Фото к услуге"
        verbose_name_plural = "Фото к услугам"

    def __str__(self) -> str:
        return self.service.title

    def delete_image_files(self):
        """Удаление файлов изображений."""

        delete_image_files.delay(str(self.image))
