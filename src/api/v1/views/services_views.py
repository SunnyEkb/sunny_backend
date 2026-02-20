from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action

from api.v1 import schemes
from api.v1 import serializers as api_serializers
from api.v1.permissions import (
    ModeratorOnly,
    PhotoOwnerOrReadOnly,
    PhotoReadOnly,
)
from api.v1.views.base_views import (
    BaseModeratorViewSet,
    BaseServiceAdViewSet,
)
from core.choices import AdvertisementStatus
from services.models import Service, ServiceImage


@extend_schema(tags=["Services"])
@extend_schema_view(
    retrieve=extend_schema(
        summary="Информация о конкретной услуге.",
        responses={
            status.HTTP_200_OK: schemes.SERVICE_RETRIEVE_OK_200,
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

    def get_queryset(self):
        queryset = Service.cstm_mng.all()
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return api_serializers.ServiceRetrieveSerializer
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

    queryset = Service.cstm_mng.filter(status=AdvertisementStatus.MODERATION)
    serializer_class = api_serializers.ServiceForModerationSerializer  # type: ignore  # noqa

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
