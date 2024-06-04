from django.db import models


class TimeCreateModel(models.Model):
    """
    Абстрактная модель с полем "Время создания".
    """

    created_at = models.DateTimeField(
        "Время создания",
        auto_now_add=True,
        null=True,
        db_index=True,
    )

    class Meta:
        abstract = True


class TimeCreateUpdateModel(TimeCreateModel):
    """
    Абстрактная модель с полями "Время создания" и "Время изменения".
    """

    updated_at = models.DateTimeField("Время изменения", auto_now=True)

    class Meta:
        abstract = True
