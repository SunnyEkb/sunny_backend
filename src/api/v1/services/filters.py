from django_filters import (
    BooleanFilter,
    CharFilter,
    ChoiceFilter,
    FilterSet,
    ModelChoiceFilter,
    RangeFilter,
)

from core.choices import ServiceCategory, ServicePlace
from services.models import Service, Type


class TypeFilter(FilterSet):
    """
    Фильтры для типов услуг.
    """

    category = ChoiceFilter(
        choices=ServiceCategory.choices, label="Категория услуги"
    )
    title = CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Тип услуги",
    )

    class Meta:
        model = Type
        fields = ("category", "title")


class ServiceFilter(FilterSet):
    """
    Фильтры для услуг.
    """

    category = ChoiceFilter(
        choices=ServiceCategory.choices,
        label="Категория услуги",
        field_name="type__category",
    )
    type = ModelChoiceFilter(
        field_name="type__title",
        to_field_name="title",
        queryset=Type.objects.all(),
        label="Тип услуги",
    )
    title = CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Название",
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

    class Meta:
        model = Service
        fields = (
            "category",
            "type",
            "title",
            "place_of_provision",
            "experience",
            "my_services",
        )

    def get_my_services(self, queryset, name, value):
        """
        Возвращает список услуг с любым статусом
        для авторизованного пользователя.
        """

        user = self.request.user
        if value is False or not user.is_authenticated:
            return queryset
        return Service.cstm_mng.filter(provider=user)
