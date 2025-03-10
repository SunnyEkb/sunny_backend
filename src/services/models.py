from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.abstract_models import (
    AbstractImage,
    BaseTypeCategory,
)
from core.base_models import AbstractAdvertisement
from core.choices import ServicePlace
from core.constants import LimitsValues
from core.enums import Limits
from services.managers import ServiceManager


class Type(BaseTypeCategory):
    """Тип услуги."""

    class Meta:
        verbose_name = "Тип услуги"
        verbose_name_plural = "Типы услуг"


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


class SubService(models.Model):
    """Позиция прайс-листа."""

    main_service = models.ForeignKey(
        to=Service,
        verbose_name="Услуга",
        on_delete=models.CASCADE,
        related_name="price_list_entries",
    )
    title = models.CharField(
        verbose_name="Наименование",
        max_length=LimitsValues.MAX_LENGTH_SUBSERVICE_TITLE,
    )
    price = models.DecimalField(
        verbose_name="Цена",
        max_digits=LimitsValues.MAX_DIGITS_PRICE,
        decimal_places=LimitsValues.DECIMAL_PLACES_PRICE,
        validators=[MinValueValidator(LimitsValues.MIN_VALUE_PRICE)],
    )

    class Meta:
        verbose_name = "Позиция прайс-листа"
        verbose_name_plural = "Позиции прайс-листов"

    def __str__(self):
        return self.title
