from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
)
from rest_framework import mixins, viewsets

from ads.models import Ad, Category
from ads.serializers import AdRetrieveSerializer, CategorySerializer
from core.choices import AdvertisementStatus


@extend_schema(
    tags=["Ads"],
)
@extend_schema_view(
    list=extend_schema(summary="Список категорий объявлений"),
)
class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Список категорий объявлений."""

    queryset = Category.objects.filter(parent=None)
    serializer_class = CategorySerializer

    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(tags=["Ads"], parameters=[OpenApiParameter("category_id", int)])
@extend_schema_view(
    list=extend_schema(summary="Список объявлений"),
)
class AdViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Объявления.
    Для получения списка объявлений необходимо указать
    query параметр "category_id".
    При отсутствии параметра будет выведен пустой список.
    """

    serializer_class = AdRetrieveSerializer

    def get_queryset(self):
        queryset = Ad.objects.filter(
            status=AdvertisementStatus.PUBLISHED.value
        )
        if self.action == "list":
            params = self.request.query_params
            if "category_id" in params:
                queryset = queryset.filter(
                    category__id=params.get("category_id")
                )
            else:
                queryset = Ad.objects.none()
        return queryset
