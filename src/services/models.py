from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model
from django.db import models

from core.choices import ServicePlace
from core.enums import Limits

User = get_user_model()


class Service(models.Model):
    """
    Услуга.
    """

    provider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Исполнитель",
    )
    titlle = models.CharField(
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
