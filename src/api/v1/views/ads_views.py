import sys

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
)
from rest_framework import (
    exceptions,
    mixins,
    status,
    viewsets,
)

from ads.models import Ad, AdImage, Category
from api.v1 import schemes
from api.v1 import serializers as api_serializers
from api.v1.paginators import CustomPaginator
from api.v1.permissions import (
    PhotoOwnerOrReadOnly,
    PhotoReadOnly,
)
from api.v1.views.base_views import BaseServiceAdViewSet
from core.choices import AdvertisementStatus, APIResponses


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
    serializer_class = api_serializers.CategorySerializer

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
        responses={
            status.HTTP_200_OK: schemes.AD_LIST_OK_200,
            status.HTTP_400_BAD_REQUEST: schemes.WRONG_PARAMETR_400,
        },
        parameters=[OpenApiParameter("category_id", int)],
    ),
    retrieve=extend_schema(
        summary="Информация о конкретном объявлении.",
        responses={
            status.HTTP_200_OK: schemes.AD_RETRIEVE_OK_200,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
    create=extend_schema(
        request=api_serializers.AdCreateUpdateSerializer,
        summary="Создание объявления.",
        examples=[schemes.AD_CREATE_UPDATE_EXAMPLE],
        responses={
            status.HTTP_201_CREATED: schemes.AD_RETRIEVE_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
    update=extend_schema(
        request=api_serializers.AdCreateUpdateSerializer,
        summary="Изменение данных объявления.",
        examples=[schemes.AD_CREATE_UPDATE_EXAMPLE],
        responses={
            status.HTTP_200_OK: schemes.AD_RETRIEVE_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
    partial_update=extend_schema(
        request=api_serializers.AdCreateUpdateSerializer,
        summary="Изменение данных объявления.",
        examples=[schemes.AD_PARTIAL_UPDATE_EXAMPLE],
        responses={
            status.HTTP_200_OK: schemes.AD_RETRIEVE_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
)
class AdViewSet(BaseServiceAdViewSet):
    """Вьюсет для объявлений."""

    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return api_serializers.AdListSerializer
        return api_serializers.AdCreateUpdateSerializer

    def get_queryset(self):
        queryset = Ad.cstm_mng.all()
        if self.action == "list":
            params = self.request.query_params
            if "category_id" in params:
                try:
                    category_id = int(params.get("category_id"))
                except ValueError:
                    raise exceptions.ValidationError(
                        detail=APIResponses.INVALID_PARAMETR.value,
                        code=status.HTTP_400_BAD_REQUEST,
                    )
                if category_id < 0:
                    raise exceptions.ValidationError(
                        detail=APIResponses.INVALID_PARAMETR.value,
                        code=status.HTTP_400_BAD_REQUEST,
                    )
                queryset = queryset.filter(
                    category__id=category_id,
                    status=AdvertisementStatus.PUBLISHED.value,
                )
            else:
                queryset = Ad.objects.none()
        return queryset


@extend_schema(
    tags=["Ads"],
    responses={
        status.HTTP_204_NO_CONTENT: None,
    },
)
@extend_schema_view(
    destroy=extend_schema(summary="Удаление фото."),
    retrieve=extend_schema(summary="Получение фото."),
    responses={
        status.HTTP_204_NO_CONTENT: None,
        status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
    },
)
class AdImageViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Фото к объявлениям."""

    queryset = AdImage.objects.all()
    serializer_class = api_serializers.AdImageRetrieveSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return (PhotoReadOnly(),)
        return (PhotoOwnerOrReadOnly(),)

    def destroy(self, request, *args, **kwargs):
        instance: AdImage = self.get_object()

        # удаляем файл
        if "test" not in sys.argv:
            instance.delete_images()

        return super().destroy(request, *args, **kwargs)
