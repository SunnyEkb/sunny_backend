from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets

from api.v1.paginators import CustomPaginator
from comments.models import Comment
from comments.serializers import CommentCreateSerializer, CommentReadSerializer


class CommentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Список комментариев к услуге."""

    pagination_class = CustomPaginator
    serializer_class = CommentReadSerializer

    def get_queryset(self):
        obj_id = self.kwargs.get("obj_id", None)
        type = self.kwargs.get("type", None)
        if obj_id and type:
            cont_type_model = get_object_or_404(
                ContentType, app_label=f"{type}s", model=f"{type}"
            )
            obj = get_object_or_404(cont_type_model.model_class(), pk=obj_id)
            return Comment.cstm_mng.filter(
                content_type=cont_type_model,
                object_id=obj.id,
            ).order_by("-created_at")
        return Comment.cstm_mng.none()


class CommentCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Создать или удалить комментарий к услуге."""

    serializer_class = CommentCreateSerializer

    def get_queryset(self):
        return Comment.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
