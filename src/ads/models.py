from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from ads.managers import AdManager
from core.choices import AdCategory
from core.enums import Limits
from core.models import AbstractAdvertisement


class Ad(AbstractAdvertisement):
    """Объявление."""

    category = models.CharField(
        verbose_name="Категория",
        choices=AdCategory,
        max_length=Limits.MAX_LENGTH_ADVMNT_CATEGORY,
    )
    price = models.DecimalField(
        "Цена",
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal(0), "Цена не может быть меньше 0"),
        ],
    )

    objects = models.Manager()
    cstm_mng = AdManager()

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"


class AdImage(models.Model):
    """Фото к объявлению."""

    image = models.ImageField("Фото к объявлению", upload_to="ads/")
    service = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        verbose_name="Объявление",
        related_name="images",
    )

    class Meta:
        verbose_name = "Фото к объявлению"
        verbose_name_plural = "Фото к объявлениям"

    def __str__(self) -> str:
        return self.service.title
