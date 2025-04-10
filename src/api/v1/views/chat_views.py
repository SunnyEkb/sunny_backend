from django.db.models import Q
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, viewsets, permissions, status

from api.v1 import schemes
from api.v1 import serializers as api_serializers
from api.v1.paginators import CustomPaginator
from chat.models import Chat


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
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        return Chat.objects.filter(
            Q(initiator=self.request.user) | Q(responder=self.request.user)
        )
