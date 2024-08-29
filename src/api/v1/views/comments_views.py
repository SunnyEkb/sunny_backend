import sys

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, viewsets, permissions, response, status
from rest_framework.decorators import action

from api.v1.paginators import CustomPaginator
from api.v1.permissions import CommentAuthorOnly
from api.v1 import schemes
from api.v1.serializers import (
    CommentImageCreateSerializer,
    CommentCreateSerializer,
    CommentReadSerializer,
)
from comments.models import Comment
from core.choices import APIResponses, CommentStatus
from core.utils import notify_about_moderation


@extend_schema(
    tags=["Comments"],
    examples=[schemes.COMMENT_LIST_EXAMPLE],
    responses={
        status.HTTP_200_OK: schemes.COMMENT_LIST_200_OK,
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
                status=CommentStatus.PUBLISHED.value,
            ).order_by("-created_at")
        return Comment.cstm_mng.none()


@extend_schema(
    tags=["Comments"],
)
@extend_schema_view(
    create=extend_schema(
        summary="Создать комментарий.",
        examples=[schemes.COMMENT_CREATE_EXAMPLE],
        responses={
            status.HTTP_201_CREATED: schemes.COMMENT_CREATED_201,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
        },
    ),
    destroy=extend_schema(
        summary="Удалить комментарий.",
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_403_FORBIDDEN: schemes.COMMENT_FORBIDDEN_403,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
        },
    ),
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
        comment: Comment = serializer.save(author=self.request.user)
        if "test" not in sys.argv:
            notify_about_moderation(comment.get_admin_url(self.request))

    def destroy(self, request, *args, **kwargs):
        instance: Comment = self.get_object()
        instance.delete_images()
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Добавить фото к комментарию.",
        methods=["POST"],
        request=CommentImageCreateSerializer,
        responses={
            status.HTTP_200_OK: schemes.COMMENT_LIST_200_OK,
            status.HTTP_400_BAD_REQUEST: schemes.CANT_ADD_PHOTO_400,
            status.HTTP_403_FORBIDDEN: schemes.COMMENT_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: schemes.CANT_ADD_PHOTO_406,
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="add_photo",
        url_name="add_photo",
        permission_classes=(CommentAuthorOnly,),
    )
    def add_photo(self, request, *args, **kwargs):
        """Добавить фото к комментарию."""

        comment: Comment = self.get_object()
        data = request.data
        img_serializer = CommentImageCreateSerializer(data=data)
        images = comment.images.all()
        if len(images) >= 5:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.MAX_IMAGE_QUANTITY_EXEED.value,
            )
        if img_serializer.is_valid():
            img_serializer.save(comment=comment)
            cmnt_serializer = CommentReadSerializer(comment)
            return response.Response(cmnt_serializer.data)
        return response.Response(
            img_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
