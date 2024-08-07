from django.db import models


class ServiceManager(models.Manager):
    """Пользовательский менеджер для модели Услуг."""

    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .select_related("provider")
            .prefetch_related("images", "comments")
        )
