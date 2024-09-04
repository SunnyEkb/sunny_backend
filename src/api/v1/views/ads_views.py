from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
)
from rest_framework import mixins, response, status, viewsets

from ads.models import Ad, Category
from api.v1.paginators import CustomPaginator
from api.v1.permissions import OwnerOrReadOnly, ReadOnly
from api.v1 import schemes
from api.v1.serializers import (
    AdRetrieveSerializer,
    AdCreateUpdateSerializer,
    CategorySerializer,
)
from core.choices import AdvertisementStatus


@extend_schema(tags=["Ads categories"])
@extend_schema_view(
    list=extend_schema(
        summary="Список категорий объявлений.",
        responses={status.HTTP_200_OK: schemes.AD_CATEGORIES_GET_OK_200},
    ),
)
class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет для категорий объявлений."""

    queryset = Category.objects.filter(parent=None)
    serializer_class = CategorySerializer

    @method_decorator(cache_page(60 * 2))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(tags=["Ads"])
@extend_schema_view(
    list=extend_schema(
        summary=(
            "Список объявлений. Для получения списка объявлений необходимо"
            " указать query "
            "параметр 'category_id'. При отсутствии параметра"
            " будет выведен пустой список."
        ),
        parameters=[OpenApiParameter("category_id", int)],
    ),
    retrieve=extend_schema(
        summary="Информация о конкретном объявлении.",
    ),
    create=extend_schema(
        request=AdCreateUpdateSerializer,
        summary="Создание объявления.",
        examples=[schemes.ADD_CREATE_EXAMPLE],
        responses={
            status.HTTP_201_CREATED: schemes.AD_CREATED_201,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
    update=extend_schema(
        request=AdCreateUpdateSerializer,
        summary="Изменение данных объявления.",
    ),
    partial_update=extend_schema(
        request=AdCreateUpdateSerializer,
        summary="Изменение данных объявления.",
    ),
)
class AdViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для объявлений."""

    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AdRetrieveSerializer
        return AdCreateUpdateSerializer

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

    def get_permissions(self):
        if self.action == "retrieve":
            return (ReadOnly(),)
        return (OwnerOrReadOnly(),)

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance: Ad = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        # смена статуса на CHANGED для повторной модерации
        instance.set_changed()
        return response.Response(serializer.data)
