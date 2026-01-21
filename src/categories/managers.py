from django.db import models


class CategoryManager(models.Manager):
    """Пользовательский менеджер для моделей категорий объявлений."""

    def get_queryset(self) -> models.QuerySet:
        """Получить запрос для данных о категориях в админке.

        :returns: запрос
        :rtype: QuerySet
        """
        return super().get_queryset().prefetch_related("subcategories")
