from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model
from django.db import models

from core.choices import ServicePlace
from core.enums import Limits
from core.models import TimeCreateUpdateModel

User = get_user_model()


class Service(TimeCreateUpdateModel):
    """
    Услуга.
    """

    provider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Исполнитель",
    )
    title = models.CharField(
        "Название", max_length=Limits.MAX_LENGTH_SERVICE_TITLE.value
    )
    description = models.TextField(
        "Описание", max_length=Limits.MAX_LENGTH_SERVICE_DESCRIPTION.value
    )
    place = ArrayField(
        models.CharField(
            max_length=Limits.MAX_LENGTH_SERVICE_PLACE.value,
            choices=ServicePlace.choices,
        ),
        verbose_name="Место оказания",
    )

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.title


class ServiceImage(models.Model):
    """
    Фото к услуге.
    """

    image = models.ImageField("Фото к услуге", upload_to="services/")
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, verbose_name="Услуга"
    )
    main_photo = models.BooleanField(
        "Основное фото",
        default=False,
    )

    class Meta:
        verbose_name = "Фото к услуге"
        verbose_name_plural = "Фото к услугам"

    def __str__(self):
        return self.service.title
