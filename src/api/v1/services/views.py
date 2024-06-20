from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets, status, pagination

from core.choices import ServiceStatus
from services.models import Service, Type
from services.serializers import (
    ServiceCreateUpdateSerializer,
    ServiceRetreiveSerializer,
    TypeGetSerializer,
)
from api.v1.permissions import OwnerOrReadOnly, ReadOnly
from api.v1.services.filters import TypeFilter
from api.v1.scheme import TYPES_GET_OK_200, TYPE_LIST_EXAMPLE

User = get_user_model()


@extend_schema(
    tags=["Types"],
    examples=[TYPE_LIST_EXAMPLE],
    responses={
        status.HTTP_200_OK: TYPES_GET_OK_200,
    },
)
@extend_schema_view(
    list=extend_schema(summary="Список типов услуг."),
)
class TypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Список типов услуг."""

    queryset = Type.objects.all()
    serializer_class = TypeGetSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TypeFilter


class ServiceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Операции с услугами."""

    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        if self.action == "list":
            return Service.cstm_mng.filter(
                status=ServiceStatus.PUBLISHED.value
            )
        return Service.cstm_mng.all()

    def get_serializer_class(self):
        if self.action in ("list", "retreive"):
            return ServiceRetreiveSerializer
        return ServiceCreateUpdateSerializer

    def get_permissions(self):
        if self.action == "retreive":
            return (ReadOnly(),)
        return (OwnerOrReadOnly(),)

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)
