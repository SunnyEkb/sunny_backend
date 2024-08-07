from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.core.validators import MaxValueValidator

from comments.models import Comment
from core.choices import ServicePlace
from core.db_utils import service_image_path, validate_image
from core.enums import Limits
from core.managers import TypeCategoryManager
from core.models import AbstractAdvertisement
from services.managers import ServiceManager
from services.tasks import delete_image_files, delete_images_dir


class Type(models.Model):
    """Тип услуги."""

    title = models.CharField(
        "Название",
        max_length=Limits.MAX_LENGTH_ADVMNT_CATEGORY,
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        verbose_name="Высшая категория",
        related_name="subcategories",
        on_delete=models.PROTECT,
        db_index=True,
    )

    objects = models.Manager()
    cstm_mng = TypeCategoryManager()

    class Meta:
        verbose_name = "Тип услуги"
        verbose_name_plural = "Тип услуги"
        ordering = ["parent_id", "id"]

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
    type = models.ManyToManyField(
        Type,
        verbose_name="Тип услуги",
        related_name="types",
    )
    price = models.JSONField("Прайс", blank=True, null=True)
    address = models.CharField(
        "Адрес",
        max_length=Limits.MAX_LENGTH_SERVICE_ADDRESS.value,
        null=True,
    )
    salon_name = models.CharField(
        "Название салона",
        max_length=Limits.MAX_LENGTH_SERVICE_SALON_NAME.value,
        null=True,
    )
    comments = GenericRelation(Comment)

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
            delete_images_dir.delay(f"services/{self.id}")


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
