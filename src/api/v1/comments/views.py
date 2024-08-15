from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, viewsets, permissions, status

from api.v1.paginators import CustomPaginator
from api.v1.permissions import CommentAuthorOnly
from api.v1.scheme import (
    COMMENT_CREATE_EXAMPLE,
    COMMENT_LIST_EXAMPLE,
    COMMENT_LIST_200_OK,
)
from comments.models import Comment
from comments.serializers import CommentCreateSerializer, CommentReadSerializer


@extend_schema(
    tags=["Comments"],
    examples=[COMMENT_LIST_EXAMPLE],
    responses={
        status.HTTP_200_OK: COMMENT_LIST_200_OK,
    },
)
@extend_schema_view(
    list=extend_schema(summary="Список комментариев."),
)
class CommentViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Список комментариев."""

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


@extend_schema(
    tags=["Comments"],
)
@extend_schema_view(
    create=extend_schema(
        summary="Создать комментарий.", examples=[COMMENT_CREATE_EXAMPLE]
    ),
    destroy=extend_schema(summary="Удалить комментарий."),
)
class CommentCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Создать или удалить комментарий."""

    serializer_class = CommentCreateSerializer

    def get_queryset(self):
        return Comment.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        return [CommentAuthorOnly()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance: Comment = self.get_object()
        instance.delete_images()
        return super().destroy(request, *args, **kwargs)
