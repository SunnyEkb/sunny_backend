from rest_framework import mixins, permissions, viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view

from api.v1.paginators import CustomPaginator
from api.v1.serializers.favorites_serializers import FavoritesSerialiser
from users.models import Favorites


@extend_schema(
    tags=["Favorites"],
)
@extend_schema_view(
    list=extend_schema(summary="Список объектов избранного."),
)
class FavoritesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Избранное."""

    serializer_class = FavoritesSerialiser
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    pagination_class = CustomPaginator

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Favorites.objects.filter(user=user)
        return Favorites.objects.none()
