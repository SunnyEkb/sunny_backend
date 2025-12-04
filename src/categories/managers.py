from django.db import models


class CategoryManager(models.Manager):
    """
    Пользовательский менеджер для моделей категорий объявлений.
    """

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().prefetch_related("subcategories")
