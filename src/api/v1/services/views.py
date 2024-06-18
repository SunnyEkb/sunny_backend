from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets, status

from services.models import Type
from services.serializers import TypeGetSerializer
from api.v1.services.filters import TypeFilter
from api.v1.scheme import TYPES_GET_OK_200, TYPE_LIST_EXAMPLE


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
