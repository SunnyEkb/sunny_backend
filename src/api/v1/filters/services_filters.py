from django.db.models import Avg, QuerySet
from django_filters import (
    BooleanFilter,
    CharFilter,
    ChoiceFilter,
    FilterSet,
    NumberFilter,
    OrderingFilter,
    RangeFilter,
)

from core.choices import AdvertisementStatus, ServicePlace
from services.models import Service


class ServiceFilter(FilterSet):
    """Фильтры для услуг."""

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
    place_of_provision = ChoiceFilter(
        choices=ServicePlace.choices,
        label="Место оказания услуги",
        field_name="place_of_provision",
    )
    experience = RangeFilter(
        field_name="experience",
        label="Опыт",
    )
    my_services = BooleanFilter(
        "provider",
        label="Список всех услуг авторизованного пользователя.",
        method="get_my_services",
    )
    address = CharFilter(
        field_name="address",
        lookup_expr="icontains",
        label="Адрес",
    )
    salon_name = CharFilter(
        field_name="salon_name",
        lookup_expr="icontains",
        label="Название салона",
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
            ("experience", "experience"),
        ),
        field_labels={
            "created_at": "Дата создания",
            "-created_at": "Дата создания (по убыванию)",
            "updated_at": "Дата последнего обновления",
            "-updated_at": "Дата последнего обновления (по убыванию)",
            "experience": "Опыт работы",
            "-experience": "Опыт работы (по убыванию)",
        },
    )

    class Meta:
        """Настройки фильтра."""

        model = Service
        fields = (
            "title",
            "description",
            "place_of_provision",
            "experience",
            "my_services",
            "address",
            "salon_name",
            "created_at",
            "updated_at",
        )

    def get_my_services(
        self, queryset: QuerySet, name: str, value: bool  # noqa: ARG002, FBT001
    ) -> QuerySet:
        """Возвращает список услуг текущего пользователя.

        Статус услуг любой.

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
        return Service.cstm_mng.filter(provider=user)

    def get_rating(
        self, queryset: QuerySet, name: str, value: int  # noqa: ARG002
    ) -> QuerySet:
        """Возвращает список услуг, c рейтингом больше value.

        Args:
            queryset (QuerySet): запрос
            name (str): название поля
            value (bool): значение параметра

        Returns:
            QuerySet: измененный запрос

        """
        return (
            Service.cstm_mng.annotate(rating=Avg("comments__rating"))
            .filter(rating__gte=value, status=AdvertisementStatus.PUBLISHED.value)
            .order_by("-created_at")
        )
