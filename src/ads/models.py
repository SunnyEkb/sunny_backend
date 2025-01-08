from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from ads.managers import AdManager
from core.abstract_models import AbstractImage
from core.base_models import AbstractAdvertisement
from core.choices import AdState
from core.enums import Limits
from core.managers import TypeCategoryManager


class Category(models.Model):
    """Категория объявления."""

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
        verbose_name = "Категория объявления"
        verbose_name_plural = "Категории объявлений"
        ordering = ["parent_id", "id"]

    def __str__(self) -> str:
        return self.title


class Ad(AbstractAdvertisement):
    """Объявление."""

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
    category = models.ManyToManyField(
        Category,
        verbose_name="Kатегории",
        related_name="ads",
    )

    objects = models.Manager()
    cstm_mng = AdManager()

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]


class AdImage(AbstractImage):
    """Фото к объявлению."""

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
