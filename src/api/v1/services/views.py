from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets, status, pagination, response
from rest_framework.decorators import action

from core.choices import APIResponses, ServiceStatus
from services.models import Service, Type
from services.serializers import (
    ServiceCreateUpdateSerializer,
    ServiceRetrieveSerializer,
    TypeGetSerializer,
)
from api.v1.permissions import OwnerOrReadOnly, ReadOnly
from api.v1.services.filters import ServiceFilter, TypeFilter
from api.v1.scheme import TYPES_GET_OK_200, TYPE_LIST_EXAMPLE
from core.utils import notify_about_moderation

User = get_user_model()


@extend_schema(
    tags=["Types"],
    examples=[TYPE_LIST_EXAMPLE],
    responses={
        status.HTTP_200_OK: TYPES_GET_OK_200,
    },
)
@extend_schema_view(
    list=extend_schema(summary="Список типов услуг"),
)
class TypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Список типов услуг."""

    queryset = Type.objects.all()
    serializer_class = TypeGetSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TypeFilter


@extend_schema(
    tags=["Services"],
)
@extend_schema_view(
    list=extend_schema(summary="Список услуг"),
    retrieve=extend_schema(summary="Информация о конкретной услуге"),
    create=extend_schema(summary="Создание услуги"),
    update=extend_schema(summary="Изменение данных услуги"),
    partial_update=extend_schema(summary="Изменение данных услуги"),
)
class ServiceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Операции с услугами."""

    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ServiceFilter

    def get_queryset(self):
        if self.action == "list":
            return Service.cstm_mng.filter(
                status=ServiceStatus.PUBLISHED.value
            )
        return Service.cstm_mng.all()

    def get_serializer_class(self):
        if self.action in ("list", "retreive"):
            return ServiceRetrieveSerializer
        return ServiceCreateUpdateSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return (ReadOnly(),)
        return (OwnerOrReadOnly(),)

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == ServiceStatus.DRAFT:
            return super().destroy(request, *args, **kwargs)
        return response.Response(
            APIResponses.CAN_NOT_DELETE_SEVICE.value,
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )

    @extend_schema(
        summary="Отменить услугу",
        methods=["POST"],
        request=None,
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="cancell",
        url_name="cancell",
        permission_classes=(OwnerOrReadOnly,),
    )
    def cancell(self, request, *args, **kwargs):
        """Отменить услугу."""

        service: Service = self.get_object()
        service.cancell()
        serializer = self.get_serializer(service)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Скрыть услугу",
        methods=["POST"],
        request=None,
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="hide",
        permission_classes=(OwnerOrReadOnly,),
    )
    def hide(self, request, *args, **kwargs):
        """Скрыть услугу."""

        service: Service = self.get_object()
        service.hide()
        serializer = self.get_serializer(service)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Отправить на модерацию",
        methods=["POST"],
        request=None,
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="moderate",
        url_name="moderate",
        permission_classes=(OwnerOrReadOnly,),
    )
    def moderate(self, request, *args, **kwargs):
        """Отправить на модерацию."""

        service: Service = self.get_object()
        service.send_to_moderation()
        print(service.get_admin_url(request))
        notify_about_moderation(service.get_admin_url(request))
        serializer = self.get_serializer(service)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Опубликовать скрытую услугу",
        methods=["POST"],
        request=None,
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="publish",
        url_name="publish",
        permission_classes=(OwnerOrReadOnly,),
    )
    def publish_hidden_service(self, request, *args, **kwargs):
        """Опубликовать скрытую услугу."""

        service: Service = self.get_object()
        service.publish()
        serializer = self.get_serializer(service)
        return response.Response(serializer.data)
