from django.db import models


class CommentManager(models.Manager):
    """Пользовательский менеджер для модели комментариев."""

    def get_queryset(self) -> models.QuerySet:
        """Сформировать запрос для комментариев.

        :returns: запрос
        :rtype: QuerySet
        """
        return (
            super().get_queryset().select_related("author").prefetch_related("images")
        )
