from django.db import models
from django.core.validators import MaxValueValidator

from core.base_models import AbstractAdvertisement, AbstractImage
from core.choices import ServicePlace
from core.enums import Limits
from core.managers import TypeCategoryManager
from services.managers import ServiceManager


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
        blank=True,
    )
    salon_name = models.CharField(
        "Название салона",
        max_length=Limits.MAX_LENGTH_SERVICE_SALON_NAME.value,
        null=True,
        blank=True,
    )

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


class ServiceImage(AbstractImage):
    """Фото к услуге."""

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
