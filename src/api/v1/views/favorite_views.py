from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions, status, viewsets

from api.v1 import schemes
from api.v1 import serializers as api_serializers
from api.v1.paginators import CustomPaginator
from users.models import Favorites


@extend_schema(
    tags=["Favorites"],
)
@extend_schema_view(
    list=extend_schema(
        summary="Список объектов избранного.",
        responses={
            status.HTTP_200_OK: schemes.FAVORITES_LIST_200_OK,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
        },
    ),
)
class FavoritesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Избранное."""

    serializer_class = api_serializers.FavoritesSerialiser
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    pagination_class = CustomPaginator

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Favorites.objects.filter(user=user)
        return Favorites.objects.none()
