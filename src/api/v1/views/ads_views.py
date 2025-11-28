import sys

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action

from ads.models import Ad, AdImage, Category
from api.v1 import schemes
from api.v1 import serializers as api_serializers
from api.v1.filters import AdFilter
from api.v1.permissions import (
    ModeratorOnly,
    PhotoOwnerOrReadOnly,
    PhotoReadOnly,
)
from api.v1.validators import validate_id
from api.v1.views.base_views import (
    BaseModeratorViewSet,
    BaseServiceAdViewSet,
    CategoryTypeViewSet,
)
from core.choices import AdvertisementStatus


@extend_schema(
    tags=["Ads"],
    responses={status.HTTP_200_OK: schemes.CATEGORIES_GET_OK_200},
)
@extend_schema_view(
    list=extend_schema(
        summary="Список категорий объявлений.",
        parameters=[OpenApiParameter("title", str)],
    ),
    retrieve=extend_schema(summary="Категория объявления."),
)
class CategoryViewSet(CategoryTypeViewSet):
    """Вьюсет для категорий объявлений."""

    def get_serializer_class(self):
        params = self.request.query_params
        if self.action == "list" and "title" in params:
            return api_serializers.CategoryGetWithoutSubCatSerializer
        return api_serializers.CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
        return self.base_get_queryset(queryset)


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
            status.HTTP_406_NOT_ACCEPTABLE: schemes.SERVICE_AD_NOT_ACCEPT_406,
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
            status.HTTP_406_NOT_ACCEPTABLE: schemes.SERVICE_AD_NOT_ACCEPT_406,
        },
    ),
    destroy=extend_schema(
        summary="Удалить объявление.",
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
)
class AdViewSet(BaseServiceAdViewSet):
    """Вьюсет для объявлений."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = AdFilter

    def get_serializer_class(self):
        if self.action == "list":
            return api_serializers.AdListSerializer
        if self.action == "retrieve":
            return api_serializers.AdRetrieveSerializer
        return api_serializers.AdCreateUpdateSerializer

    def get_queryset(self):
        queryset = Ad.cstm_mng.all()
        if self.action == "list":
            params = self.request.query_params
            if "category_id" in params:
                category_id = params.get("category_id")
                validate_id(category_id)
                queryset = queryset.filter(
                    category__id=category_id,
                    status=AdvertisementStatus.PUBLISHED,
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
            instance.delete_image_files()

        return super().destroy(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(
        summary="Список объявлений для модерации.",
        responses={
            status.HTTP_200_OK: schemes.AD_LIST_FOR_MODERATION_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
)
class AdModerationViewSet(BaseModeratorViewSet):
    """Модерация объявлений."""

    queryset = Ad.cstm_mng.filter(status=AdvertisementStatus.MODERATION)
    serializer_class = api_serializers.AdForModerationSerializer  # type: ignore  # noqa

    def _get_receiver(self):
        return self.get_object().provider

    @extend_schema(
        summary="Одобрить объявление.",
        request=None,
        methods=["POST"],
        responses={
            status.HTTP_200_OK: schemes.OBJ_APPROVED_200_OK,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="approve",
        url_name="approve",
        permission_classes=(ModeratorOnly,),
    )
    def approve(self, request, *args, **kwargs):
        return super().approve(request, *args, **kwargs)

    @extend_schema(
        summary="Отклонить объявление.",
        request=None,
        methods=["POST"],
        responses={
            status.HTTP_200_OK: schemes.OBJ_REJECTED_200_OK,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="reject",
        url_name="reject",
        permission_classes=(ModeratorOnly,),
    )
    def reject(self, request, *args, **kwargs):
        return super().reject(request, *args, **kwargs)
