from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action

from api.v1 import schemes
from api.v1 import serializers as api_serializers
from api.v1.filters import ServiceFilter
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
from services.models import Service, ServiceImage, Type


@extend_schema(
    tags=["Services types"],
    responses={status.HTTP_200_OK: schemes.TYPES_GET_OK_200},
)
@extend_schema_view(
    list=extend_schema(
        summary="Список типов услуг.",
        parameters=[OpenApiParameter("title", str)],
    ),
    retrieve=extend_schema(summary="Тип услуги."),
)
class TypeViewSet(CategoryTypeViewSet):
    """Список типов услуг."""

    def get_queryset(self):
        queryset = Type.objects.all()
        return self.base_get_queryset(queryset)

    def get_serializer_class(self):
        params = self.request.query_params
        if "title" in params:
            return api_serializers.TypeGetWithoutSubCatSerializer
        return api_serializers.TypeGetSerializer


@extend_schema(
    tags=["Services"],
)
@extend_schema_view(
    list=extend_schema(
        summary=(
            "Список услуг. Для получения списка услуг по категориям необходимо"
            " указать query параметр 'type_id'."
        ),
        parameters=[OpenApiParameter("type_id", int)],
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
            status.HTTP_400_BAD_REQUEST: schemes.WRONG_PARAMETR_400,
        },
    ),
    retrieve=extend_schema(
        summary="Информация о конкретной услуге.",
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
    create=extend_schema(
        request=api_serializers.ServiceCreateUpdateSerializer,
        summary="Создание услуги.",
        responses={
            status.HTTP_201_CREATED: schemes.SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
        },
        examples=[schemes.SERVICE_CREATE_UPDATE_EXAMPLE],
    ),
    update=extend_schema(
        request=api_serializers.ServiceCreateUpdateSerializer,
        summary="Изменение данных услуги.",
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: schemes.SERVICE_AD_NOT_ACCEPT_406,
        },
        examples=[schemes.SERVICE_CREATE_UPDATE_EXAMPLE],
    ),
    partial_update=extend_schema(
        request=api_serializers.ServiceCreateUpdateSerializer,
        summary="Изменение данных услуги.",
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: schemes.SERVICE_AD_NOT_ACCEPT_406,
        },
        examples=[schemes.SERVICE_PARTIAL_UPDATE_EXAMPLE],
    ),
    destroy=extend_schema(
        summary="Удалить услугу.",
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
)
class ServiceViewSet(BaseServiceAdViewSet):
    """Операции с услугами."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = ServiceFilter

    def get_queryset(self):
        queryset = Service.cstm_mng.all()
        if self.action == "list":
            params = self.request.query_params
            queryset = queryset.filter(
                status=AdvertisementStatus.PUBLISHED.value
            )
            if "type_id" in params:
                type_id = params.get("type_id")
                validate_id(type_id)
                queryset = queryset.filter(type__id=type_id)
        return queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return api_serializers.ServiceListSerializer
        return api_serializers.ServiceCreateUpdateSerializer


@extend_schema(
    tags=["Services"],
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
class ServiceImageViewSet(
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Фото к услугам."""

    queryset = ServiceImage.objects.all()
    serializer_class = api_serializers.ServiceImageRetrieveSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return (PhotoReadOnly(),)
        return (PhotoOwnerOrReadOnly(),)

    def destroy(self, request, *args, **kwargs):
        instance: ServiceImage = self.get_object()

        # удаляем файл
        instance.delete_image_files()

        return super().destroy(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(
        summary="Список услуг для модерации.",
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_FOR_MODERATION_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
)
class ServiceModerationViewSet(BaseModeratorViewSet):
    """Модерация услуг."""

    queryset = Service.cstm_mng.filter(
        status=AdvertisementStatus.MODERATION.value
    )
    serializer_class = api_serializers.ServiceForModerationSerializer

    def _get_receiver(self):
        return self.get_object().provider

    @extend_schema(
        summary="Одобрить услугу.",
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
        summary="Отклонить услугу.",
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
