from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from ads.managers import AdManager
from core.choices import AdCategory, AdState
from core.db_utils import ad_image_path, validate_image
from core.enums import Limits
from core.models import AbstractAdvertisement


class Ad(AbstractAdvertisement):
    """Объявление."""

    category = models.CharField(
        "Категория",
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
    condition = models.CharField(
        "Состояние",
        choices=AdState,
        max_length=Limits.MAX_LENGTH_ADVMNT_STATE,
        default=AdState.USED.value,
    )

    objects = models.Manager()
    cstm_mng = AdManager()

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"


class AdImage(models.Model):
    """Фото к объявлению."""

    image = models.ImageField(
        "Фото к объявлению",
        upload_to=ad_image_path,
        validators=[validate_image],
    )
    ad = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        verbose_name="Объявление",
        related_name="images",
    )

    class Meta:
        verbose_name = "Фото к объявлению"
        verbose_name_plural = "Фото к объявлениям"

    def __str__(self) -> str:
        return self.ad.title
