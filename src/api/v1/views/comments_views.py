from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, viewsets, permissions, response, status
from rest_framework.decorators import action

from api.v1 import schemes
from api.v1 import serializers as api_serializers
from api.v1.paginators import CustomPaginator
from api.v1.permissions import CommentAuthorOnly, ModeratorOnly
from config.settings.base import ALLOWED_IMAGE_FILE_EXTENTIONS
from comments.exceptions import WrongObjectType
from comments.models import Comment
from core.choices import APIResponses, CommentStatus


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
class CommentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Список комментариев."""

    pagination_class = CustomPaginator
    serializer_class = api_serializers.CommentReadSerializer

    def get_queryset(self):
        obj_id = self.kwargs.get("obj_id", None)
        type = self.kwargs.get("type", None)
        if type not in ["ad", "service"]:
            raise WrongObjectType()
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

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except WrongObjectType:
            return response.Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=APIResponses.WRONG_OBJECT_TYPE,
            )


@extend_schema(tags=["Comments"])
@extend_schema_view(
    destroy=extend_schema(
        summary="Удалить комментарий.",
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.COMMENT_FORBIDDEN_403,
        },
    ),
)
class CommentCreateDestroyViewSet(
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Удалить комментарий и добавить к нему фото."""

    serializer_class = api_serializers.CommentReadSerializer

    def get_queryset(self):
        return Comment.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        return [CommentAuthorOnly()]

    def destroy(self, request, *args, **kwargs):
        instance: Comment = self.get_object()
        instance.delete_images()
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Добавить фото к комментарию.",
        methods=["POST"],
        request=api_serializers.CommentImageCreateSerializer,
        responses={
            status.HTTP_200_OK: schemes.COMMENT_LIST_200_OK,
            status.HTTP_400_BAD_REQUEST: schemes.CANT_ADD_PHOTO_400,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.COMMENT_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: schemes.CANT_ADD_PHOTO_406,
        },
        examples=[schemes.UPLOAD_FILE_EXAMPLE],
        description=(
            "Файл принимается строкой, закодированной в base64. Допустимые "
            f"расширения файла - {', '.join(ALLOWED_IMAGE_FILE_EXTENTIONS)}."
        ),
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="add-photo",
        url_name="add_photo",
        permission_classes=(CommentAuthorOnly,),
    )
    def add_photo(self, request, *args, **kwargs):
        """Добавить фото к комментарию."""

        comment: Comment = self.get_object()
        data = request.data
        img_serializer = api_serializers.CommentImageCreateSerializer(
            data=data
        )
        images = comment.images.all()
        if len(images) >= 5:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.MAX_IMAGE_QUANTITY_EXEED.value,
            )
        if img_serializer.is_valid():
            img_serializer.save(comment=comment)
            cmnt_serializer = api_serializers.CommentReadSerializer(comment)
            return response.Response(cmnt_serializer.data)
        return response.Response(
            img_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=["Moderator"])
@extend_schema_view(
    list=extend_schema(
        summary="Список комментариев для модерации.",
        responses={
            status.HTTP_200_OK: schemes.COMMENT_LIST_FOR_MODERATION_200_OK,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
)
class CommentModerationViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Модерация комментариев."""

    queryset = Comment.cstm_mng.filter(
        status=CommentStatus.MODERATION.value
    ).order_by("-created_at")
    serializer_class = api_serializers.CommentForModerationSerializer
    permission_classes = (ModeratorOnly,)
    pagination_class = CustomPaginator

    def _get_receiver(self):
        return self.get_object().author

    @extend_schema(
        summary="Одобрить комментарий.",
        request=None,
        methods=["POST"],
        responses={
            status.HTTP_200_OK: schemes.OBJ_APPROVED_200_OK,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="approve",
        url_name="approve",
        permission_classes=(ModeratorOnly,),
    )
    def approve(self, request, *args, **kwargs):
        """Одобрить."""

        object = self.get_object()
        object.approve()
        return response.Response(
            status=status.HTTP_200_OK,
            data=APIResponses.OBJECT_APPROVED.value,
        )

    @extend_schema(
        summary="Отклонить комментарий.",
        request=None,
        methods=["POST"],
        responses={
            status.HTTP_200_OK: schemes.OBJ_REJECTED_200_OK,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="reject",
        url_name="reject",
        permission_classes=(ModeratorOnly,),
    )
    def reject(self, request, *args, **kwargs):
        object = self.get_object()
        object.reject()
        return response.Response(
            status=status.HTTP_200_OK,
            data=APIResponses.OBJECT_REJECTED.value,
        )
