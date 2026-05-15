from typing import TYPE_CHECKING

from django.db.models import Q
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, permissions, status, viewsets

from api.v1 import schemes
from api.v1 import serializers as api_serializers
from api.v1.paginators import CustomPaginator
from chat.models import Chat

if TYPE_CHECKING:
    from django.db.models import QuerySet


@extend_schema(
    tags=["Chats"],
    examples=[schemes.CHAT_EXAMPLE],
    responses={status.HTTP_200_OK: schemes.CHATS_LIST_200_OK},
)
@extend_schema_view(list=extend_schema(summary="Список чатов."))
class ChatViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Список чатов пользователя."""

    pagination_class = CustomPaginator
    serializer_class = api_serializers.ChatSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> "QuerySet":
        """Изменить запрос по умолчанию."""
        return Chat.objects.filter(
            Q(buyer=self.request.user) | Q(seller=self.request.user)
        )
