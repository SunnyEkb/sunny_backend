from django.db.models import Avg, QuerySet
from django_filters import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    NumberFilter,
    OrderingFilter,
)

from ads.models import Ad
from core.choices import AdvertisementStatus


class AdFilter(FilterSet):
    """Фильтры для объявлений."""

    title = CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Название",
    )
    description = CharFilter(
        field_name="description",
        lookup_expr="icontains",
        label="Описание",
    )
    my_ads = BooleanFilter(
        "provider",
        label="Список всех услуг авторизованного пользователя.",
        method="get_my_ads",
    )
    rating = NumberFilter(
        field_name="rating",
        label="Рейтинг от",
        method="get_rating",
    )
    ordering = OrderingFilter(
        fields=(
            ("created_at", "created_at"),
            ("updated_at", "updated_at"),
        ),
        field_labels={
            "created_at": "Дата создания",
            "-created_at": "Дата создания (по убыванию)",
            "updated_at": "Дата последнего обновления",
            "-updated_at": "Дата последнего обновления (по убыванию)",
        },
    )

    class Meta:
        """Настройки фильтра."""

        model = Ad
        fields = (
            "title",
            "description",
            "my_ads",
            "rating",
            "created_at",
            "updated_at",
        )

    def get_my_ads(
        self, queryset: QuerySet, name: str, value: bool  # noqa: ARG002, FBT001
    ) -> QuerySet:
        """Возвращает список объявлений текущего пользователя.

        Статус объявлений любой.

        Args:
            queryset (QuerySet): запрос
            name (str): название поля
            value (bool): значение параметра

        Returns:
            QuerySet: измененный запрос

        """
        user = self.request.user
        if value is False or not user.is_authenticated:
            return queryset
        return Ad.cstm_mng.filter(provider=user)

    def get_rating(
        self, queryset: QuerySet, name: str, value: int  # noqa: ARG002
    ) -> QuerySet:
        """Возвращает список объявлений, с рейтингом больше value.

        Args:
            queryset (QuerySet): запрос
            name (str): название поля
            value (int): значение рейтнига

        Returns:
            QuerySet: измененный запрос

        """
        return (
            Ad.cstm_mng.annotate(rating=Avg("comments__rating"))
            .filter(rating__gte=value, status=AdvertisementStatus.PUBLISHED.value)
            .order_by("-created_at")
        )
