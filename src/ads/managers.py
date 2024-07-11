from django.db import models


class AdManager(models.Manager):
    """Пользовательский менеджер для модели Объявлений."""

    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .select_related("provider")
            .prefetch_related("images")
        )
