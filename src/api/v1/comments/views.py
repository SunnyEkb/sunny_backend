from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets

from api.v1.paginators import CustomPaginator
from comments.models import Comment
from comments.serializers import CommentReadSerializer
from services.models import Service


class CommentViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Комментарии к услуге."""

    pagination_class = CustomPaginator
    serializer_class = CommentReadSerializer

    def get_queryset(self):
        service: Service = get_object_or_404(
            Service, pk=self.kwargs.get("service_id")
        )
        queryset = Comment.cstm_mng.filter(
            content_type=ContentType.objects.get(
                app_label="services", model="service"
            ),
            object_id=service.id,
        )
        return queryset
