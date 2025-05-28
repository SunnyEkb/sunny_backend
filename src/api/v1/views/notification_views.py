from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, permissions, response, status, viewsets
from rest_framework.decorators import action

from api.v1 import serializers as api_serializers
from api.v1 import schemes
from api.v1.paginators import CustomPaginator
from api.v1.permissions import NotificationRecieverOnly
from core.choices import APIResponses
from notifications.models import Notification


@extend_schema(
    tags=["Notifications"],
)
@extend_schema_view(
    list=extend_schema(
        summary="Список Уведомлений.",
        responses={
            status.HTTP_200_OK: schemes.NOTIFICATIONS_LIST_200_OK,
        },
    ),
)
class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Список уведомлений."""

    serializer_class = api_serializers.NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPaginator

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user)

    @extend_schema(
        summary="Пометить прочитанным.",
        request=None,
        methods=["POST"],
        responses={
            status.HTTP_200_OK: schemes.NOTIFICATION_MARKED_AS_READ_200_OK,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="mark-as-read",
        url_name="mark_as_read",
        permission_classes=(NotificationRecieverOnly,),
    )
    def mark_as_read(self, request, *args, **kwargs):
        """Пометить прочитанным."""

        obj: Notification = self.get_object()
        obj.mark_as_read()
        return response.Response(
            status=status.HTTP_200_OK,
            data=APIResponses.NOTIFICATION_IS_READ.value,
        )

    @extend_schema(
        summary="Пометить непрочитанным.",
        request=None,
        methods=["POST"],
        responses={
            status.HTTP_200_OK: schemes.NOTIFICATION_MARKED_AS_UNREAD_200_OK,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="mark-as-unread",
        url_name="mark_as_unread",
        permission_classes=(NotificationRecieverOnly,),
    )
    def mark_as_unread(self, request, *args, **kwargs):
        """Пометить непрочитанным."""

        obj: Notification = self.get_object()
        obj.mark_as_unread()
        return response.Response(
            status=status.HTTP_200_OK,
            data=APIResponses.NOTIFICATION_IS_UNREAD.value,
        )
