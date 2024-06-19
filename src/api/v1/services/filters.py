from django_filters import CharFilter, ChoiceFilter, FilterSet

from core.choices import ServiceCategory
from services.models import Type


class TypeFilter(FilterSet):
    """
    Фильтры для типов услуг.
    """

    category = ChoiceFilter(
        choices=ServiceCategory.choices, label="Категория Услуги"
    )
    title = CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Тип услуги.",
    )

    class Meta:
        model = Type
        fields = ("category", "title")
