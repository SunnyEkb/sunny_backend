from django.db import models


class TypeCategoryManager(models.Manager):
    """
    Пользовательский менеджер для моделей категорий объявлений и типов услуг.
    """

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().prefetch_related("subcategories")
