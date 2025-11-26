from django.db import models

from categories.managers import CategoryManager
from core.db_utils import validate_svg
from core.enums import Limits


class Category(models.Model):
    """Категория объявлений сервиса."""

    title = models.CharField(
        "Название",
        max_length=Limits.MAX_LENGTH_CATEGORY_TITLE,
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
    image = models.FileField(
        "изображение",
        upload_to="categories/",
        validators=[validate_svg],
        blank=True,
        null=True,
    )

    objects = models.Manager()
    cstm_mng = CategoryManager()

    class Meta:
        verbose_name = "Категория объявления"
        verbose_name_plural = "Категории объявлений"
        ordering = ["parent_id", "id"]

    def __str__(self) -> str:
        """Получение строкового представления категории.

        :return: строковое представление категории
        :rtype: str
        """

        return self.title
