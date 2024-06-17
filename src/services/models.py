from django.contrib.auth import get_user_model
from django.db import models

from core.choices import ServiceCategory, ServicePlace, ServiceStatus
from core.enums import Limits
from core.models import TimeCreateUpdateModel
from services.managers import ServiceManager

User = get_user_model()


class Type(models.Model):
    """Тип услуги."""

    title = models.CharField(
        "Название",
        max_length=Limits.MAX_LENGTH_TYPE_TITLE.value,
    )

    category = models.CharField(
        "Вид услуги",
        max_length=Limits.MAX_LENGTH_SERVICE_CATEGORY.value,
        choices=ServiceCategory,
    )

    class Meta:
        verbose_name = "Тип услуги"
        verbose_name_plural = "Типы услуг"
        index_together = ["category", "title"]
        ordering = ["category", "title"]

    def __str__(self) -> str:
        return self.title


class Service(TimeCreateUpdateModel):
    """Услуга."""

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
    experience = models.PositiveIntegerField(
        "Опыт",
        default=0
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
    status = models.IntegerField(
        "Статус услуги",
        choices=ServiceStatus.choices,
        default=ServiceStatus.DRAFT.value
    )

    objects = models.Manager()
    cstm_mng = ServiceManager()

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.title

    def hide(self):
        if self.status == ServiceStatus.PUBLISHED.value:
            self.status = ServiceStatus.HIDDEN.value
            self.save()

    def send_to_moderation(self):
        if self.status == ServiceStatus.DRAFT.value:
            self.status = ServiceStatus.MODERATION.value
            self.save()

    def publish(self):
        if self.status == ServiceStatus.MODERATION.value:
            self.status = ServiceStatus.PUBLISHED.value
            self.save()


class ServiceImage(models.Model):
    """Фото к услуге."""

    image = models.ImageField("Фото к услуге", upload_to="services/")
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

    def __str__(self):
        return self.service.title
