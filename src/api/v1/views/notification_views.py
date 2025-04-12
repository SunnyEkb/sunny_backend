from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action

from api.v1 import serializers as api_serializers
from api.v1.paginators import CustomPaginator
from api.v1.permissions import NotificationRecieverOnly
from notifications.models import Notification


@extend_schema(
    tags=["Notifications"],
)
@extend_schema_view(
    list=extend_schema(summary="Список Уведомлений."),
)
class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Список уведомлений."""

    serializer_class = api_serializers.NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPaginator

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.reqest.user)

    @extend_schema(
        summary="Пометить прочитанным.",
        request=None,
        methods=["POST"],
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="mark_as_read",
        url_name="mark_as_read",
        permission_classes=(NotificationRecieverOnly,),
    )
    def approve(self, request, *args, **kwargs):
        """Пометить прочитанным."""

        pass
