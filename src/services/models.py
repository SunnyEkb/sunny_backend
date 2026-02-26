from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from categories.models import Category
from core.abstract_models import AbstractImage
from core.base_models import AbstractAdvertisement
from core.choices import ServicePlace
from core.constants import LimitsValues
from core.enums import Limits
from services.managers import ServiceManager


class Service(AbstractAdvertisement):
    """Услуга."""

    experience = models.PositiveIntegerField(
        "Опыт",
        default=0,
        validators=[MaxValueValidator(Limits.MAXIMUM_EXPERIENCE)],
    )
    place_of_provision = models.CharField(
        "Место оказания услуги",
        max_length=Limits.MAX_LENGTH_SERVICE_PLACE,
        choices=ServicePlace.choices,
        default=ServicePlace.OPTIONS,
    )
    category = models.ManyToManyField(
        Category,
        verbose_name="Категория",
        related_name="services",
    )
    salon_name = models.CharField(  # noqa: DJ001
        "Название салона",
        max_length=Limits.MAX_LENGTH_SERVICE_SALON_NAME,
        null=True,
        blank=True,
    )

    objects = models.Manager()
    cstm_mng = ServiceManager()

    class Meta:
        """Настройки модели услуг."""

        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["-created_at"]  # noqa: RUF012
        default_related_name = "services"


class ServiceImage(AbstractImage):
    """Фото к услуге."""

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name="Услуга",
        related_name="images",
    )

    class Meta:
        """Настройки модели фото к услуге."""

        verbose_name = "Фото к услуге"
        verbose_name_plural = "Фото к услугам"

    def __str__(self) -> str:
        """Получить строковое представление фото к услуге.

        Returns:
            str: строковое представление фото к услуге

        """
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
        """Настройки модели позиция прайс-листа."""

        verbose_name = "Позиция прайс-листа"
        verbose_name_plural = "Позиции прайс-листов"

    def __str__(self) -> str:
        """Получить строковое представление позиции прайс-листа.

        Returns:
            str: нимаенование позиции прайс-листа

        """
        return self.title
