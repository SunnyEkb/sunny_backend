from typing import TYPE_CHECKING, List  # noqa: UP035

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.db.transaction import atomic
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import (
    mixins,
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from ads.models import Ad
from api.v1 import schemes
from api.v1 import serializers as api_serializers
from api.v1.paginators import CustomPaginator
from api.v1.permissions import ModeratorOnly, OwnerOrReadOnly, ReadOnly
from bad_word_filter.tasks import moderate_comment_task
from comments.models import Comment
from config.settings.base import ALLOWED_IMAGE_FILE_EXTENTIONS
from core.choices import AdvertisementStatus, APIResponses, Notifications
from core.enums import Limits
from notifications.models import Notification
from services.models import Service
from users.models import Favorites

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request
    from rest_framework.serializers import Serializer


class BaseServiceAdViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый вьюсет для услуг и объявлений."""

    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    serializer_class = None

    def get_permissions(self) -> permissions.BasePermission:
        if self.action == "retrieve":
            return (ReadOnly(),)
        if self.action in [
            "add_to_favorites",
            "delete_from_favorites",
            "add_comment",
        ]:
            return (permissions.IsAuthenticated(),)
        return (OwnerOrReadOnly(),)

    def perform_create(self, serializer: "Serializer") -> None:
        serializer.save(provider=self.request.user)

    def update(
        self, request: "Request", *args: list, **kwargs: dict  # noqa: ARG002
    ) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Проверяем, что объект не находится на модерации
        if instance.status == AdvertisementStatus.MODERATION:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.AD_OR_SERVICE_IS_UNDER_MODERATION,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}  # noqa: SLF001

        # смена статуса на DRAFT для повторной модерации
        instance.set_draft()
        return Response(serializer.data)

    def destroy(self, request: "Request", *args: list, **kwargs: dict) -> Response:
        instance = self.get_object()
        instance.delete_images()
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Скрыть услугу или объявление.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: (schemes.CANT_HIDE_SERVICE_OR_AD_406),
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="hide",
        url_name="hide",
        permission_classes=(OwnerOrReadOnly,),
    )
    def hide(
        self, request: "Request", *args: list, **kwargs: dict  # noqa: ARG002
    ) -> Response:
        """Скрыть услугу или объявление."""
        obj = self.get_object()
        if obj.status != AdvertisementStatus.PUBLISHED:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.CAN_NOT_HIDE_SERVICE_OR_AD,
            )
        obj.hide()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    @extend_schema(
        summary="Опубликовать услугу или объявление.",
        description=(
            "Если услуга (объявление) имеет статус 'HIDDEN', она публикуется.",
            "Если статус 'DRAFT', она на модерацию.",
        ),
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_200_OK: schemes.AD_SERVICE_SENT_TO_MODERATION,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: (schemes.CANT_PUBLISH_SERVICE_OR_AD_406),
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="publish",
        url_name="publish",
        permission_classes=(OwnerOrReadOnly,),
    )
    def publish_object(
        self, request: "Request", *args: list, **kwargs: dict  # noqa: ARG002
    ) -> Response:
        """Опубликовать услугу или объявление."""
        obj = self.get_object()
        obj_status = obj.status
        if obj_status not in [
            AdvertisementStatus.DRAFT,
            AdvertisementStatus.HIDDEN,
        ]:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.SERVICE_OR_AD_CANT_BE_PUBLISHED,
            )
        obj.publish(request)
        if obj_status == AdvertisementStatus.HIDDEN:
            serializer = self.get_serializer(obj)
            return Response(serializer.data)
        return Response(APIResponses.AD_OR_SERVICE_SENT_MODERATION)

    @extend_schema(
        summary="Добавить фото к услуге.",
        methods=["POST"],
        request=api_serializers.AdImagesSerializer,
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
            status.HTTP_400_BAD_REQUEST: schemes.CANT_ADD_PHOTO_400,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
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
        permission_classes=(OwnerOrReadOnly,),
    )
    def add_photo(  # noqa: C901, PLR0912
        self, request: "Request", *args: list, **kwargs: dict  # noqa: ARG002
    ) -> Response:
        """Добавить фото к услуге (объявлению)."""
        obj = self.get_object()

        # Проверяем, что объект не находится на модерации
        if obj.status == AdvertisementStatus.MODERATION:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.AD_OR_SERVICE_IS_UNDER_MODERATION,
            )

        # Проверяем, чтобы количество фото было не больше максимума
        images = obj.images.all()
        if len(images) + len(request.data["images"]) >= Limits.MAX_FILE_QUANTITY:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.MAX_IMAGE_QUANTITY_EXEED,
            )

        data = request.data
        # Определяем необходимый сериализатор
        if isinstance(obj, Service):
            img_serializer = api_serializers.ServiceImagesSerializer(data=data)
        elif isinstance(obj, Ad):
            img_serializer = api_serializers.AdImagesSerializer(data=data)

        if img_serializer.is_valid():
            if isinstance(img_serializer, api_serializers.ServiceImagesSerializer):
                for image in img_serializer.validated_data["images"]:
                    photo_serializer = api_serializers.ServiceImageCreateSerializer(
                        data=image
                    )
                    if photo_serializer.is_valid(raise_exception=True):
                        if images.filter(title_photo=True).exists():
                            photo_serializer.save(service=obj)
                        else:
                            photo_serializer.save(service=obj, title_photo=True)
            else:
                for image in img_serializer.validated_data["images"]:
                    photo_serializer = api_serializers.AdImageCreateSerializer(
                        data=image
                    )
                    if photo_serializer.is_valid(raise_exception=True):
                        if images.filter(title_photo=True).exists():
                            photo_serializer.save(ad=obj)
                        else:
                            photo_serializer.save(ad=obj, title_photo=True)
            obj.set_draft()
            obj_serializer = self.get_serializer(obj)
            return Response(obj_serializer.data)
        return Response(img_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Добавить в избранное.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_201_CREATED: schemes.ADDED_TO_FAVORITES_201,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_406_NOT_ACCEPTABLE: (schemes.CANT_ADD_TO_FAVORITES_406),
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="add-to-favorites",
        url_name="add_to_favorites",
        permission_classes=(permissions.IsAuthenticated),
    )
    def add_to_favorites(
        self, request: "Request", *args: list, **kwargs: dict  # noqa: ARG002
    ) -> Response:
        """Добавить в избранное."""
        obj = self.get_object()
        if obj.status != AdvertisementStatus.PUBLISHED:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_IS_NOT_PUBLISHED,
            )

        if isinstance(obj, Service):
            app_label = "services"
            model = "service"
        else:
            app_label = "ads"
            model = "ad"

        if Favorites.objects.filter(
            content_type=ContentType.objects.get(app_label=app_label, model=model),
            object_id=obj.id,
            user=request.user,
        ).exists():
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_ALREADY_IN_FAVORITES,
            )
        if obj.provider == request.user:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_PROVIDER_CANT_ADD_TO_FAVORITE,
            )
        Favorites.objects.create(
            content_type=ContentType.objects.get(app_label=app_label, model=model),
            object_id=obj.id,
            user=request.user,
        )
        return Response(
            status=status.HTTP_201_CREATED,
            data=APIResponses.ADDED_TO_FAVORITES,
        )

    @extend_schema(
        summary="Добавить комментарий.",
        methods=["POST"],
        request=api_serializers.CommentCreateSerializer,
        responses={
            status.HTTP_201_CREATED: schemes.COMMENT_CREATED_201,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.COMMENT_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: schemes.OBJECT_IS_NOT_PUBLISED_406,
        },
        examples=[schemes.COMMENT_CREATE_EXAMPLE],
        description=(
            'Поле "images" не является обязательным. '
            "Фото принимаются строкой, закодированной в base64. Допустимые "
            f"расширения файла - {', '.join(ALLOWED_IMAGE_FILE_EXTENTIONS)}."
        ),
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="add-comment",
        url_name="add_comment",
        permission_classes=(permissions.IsAuthenticated),
    )
    def add_comment(
        self, request: "Request", *args: list, **kwargs: dict  # noqa: ARG002
    ) -> Response:
        """Добавить комментарий."""
        serializer = api_serializers.CommentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        obj = self.get_object()
        if obj.status != AdvertisementStatus.PUBLISHED:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_IS_NOT_PUBLISHED,
            )

        if isinstance(obj, Service):
            app_label = "services"
            model = "service"
        else:
            app_label = "ads"
            model = "ad"

        if Comment.objects.filter(
            content_type=ContentType.objects.get(app_label=app_label, model=model),
            object_id=obj.id,
            author=request.user,
        ).exists():
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.COMMENT_ALREADY_EXISTS,
            )
        if obj.provider == request.user:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.COMMENTS_BY_PROVIDER_PROHIBITED,
            )

        comment: Comment = serializer.save(
            content_type=ContentType.objects.get(app_label=app_label, model=model),
            object_id=obj.id,
            author=request.user,
        )
        moderate_comment_task.delay_on_commit(comment_id=comment.id)
        return Response(
            status=status.HTTP_201_CREATED,
            data=APIResponses.COMMENT_ADDED,
        )

    @extend_schema(
        summary="Удалить из избранного.",
        methods=["DELETE"],
        request=None,
        responses={
            status.HTTP_204_NO_CONTENT: (schemes.DELETED_FROM_FAVORITES_204),
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_406_NOT_ACCEPTABLE: (schemes.CANT_DELETE_FROM_FAVORITES_406),
        },
    )
    @action(
        detail=True,
        methods=("delete",),
        url_path="delete-from-favorites",
        url_name="delete_from_favorites",
        permission_classes=(permissions.IsAuthenticated),
    )
    def delete_from_favorites(
        self, request: "Request", *args: list, **kwargs: dict  # noqa: ARG002
    ) -> Response:
        """Удалить из избранного."""
        obj = self.get_object()

        if isinstance(obj, Service):
            app_label = "services"
            model = "service"
        else:
            app_label = "ads"
            model = "ad"

        if not Favorites.objects.filter(
            content_type=ContentType.objects.get(app_label=app_label, model=model),
            object_id=obj.id,
            user=request.user,
        ).exists():
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_NOT_IN_FAVORITES,
            )
        Favorites.objects.get(
            content_type=ContentType.objects.get(app_label=app_label, model=model),
            object_id=obj.id,
            user=request.user,
        ).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
            data=APIResponses.DELETED_FROM_FAVORITES,
        )


class CategoryTypeViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Базовый вьюсет для типов услуг и объявлений."""

    serializer_class = None

    @method_decorator(cache_page(60 * 2))
    def list(self, request: "Request", *args: list, **kwargs: dict) -> Response:
        """Получить список объектов."""
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 2))
    def retrieve(
        self, request: "Request", *args: List, **kwargs: dict  # noqa: UP006
    ) -> Response:
        """Получить объект."""
        return super().retrieve(request, *args, **kwargs)

    def base_get_queryset(self, queryset: "QuerySet") -> "QuerySet":
        """Изменить запрос к БД по умолчанию.

        Args:
            queryset (QuerySet): запрос к БД

        Returns:
            QuerySet: измененный запрос к БД

        """
        if self.action == "list":
            params = self.request.query_params
            if "title" in params:
                title = params.get("title")
                queryset = queryset.filter(title__icontains=title)
            else:
                queryset = queryset.filter(parent=None)
        return queryset


@extend_schema(tags=["Moderator"])
class BaseModeratorViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый вьюсет для модерации комментариев, услуг и объявлений."""

    pagination_class = CustomPaginator
    serializer_class = None
    permission_classes = (ModeratorOnly,)

    def approve(
        self, request: "Request", *args: list, **kwargs: dict  # noqa: ARG002
    ) -> Response:
        """Одобрить."""
        obj = self.get_object()
        with atomic():
            self._create_notification(text=Notifications.APPROVE_OBJECT)
            obj.approve()
        return Response(
            status=status.HTTP_200_OK,
            data=APIResponses.OBJECT_APPROVED,
        )

    def reject(
        self, request: "Request", *args: list, **kwargs: dict  # noqa: ARG002
    ) -> Response:
        """Отклонить."""
        obj = self.get_object()
        with atomic():
            self._create_notification(text=Notifications.REJECT_OBJECT)
            obj.reject()
        return Response(
            status=status.HTTP_200_OK,
            data=APIResponses.OBJECT_REJECTED,
        )

    def _create_notification(self, text: str) -> None:
        """Создать уведомление в БД.

        Args:
            text (str): текст уведомления

        """
        Notification.objects.create(
            link=self._get_url(), receiver=self._get_receiver(), text=text
        )

    def _get_url(self) -> str:
        """Создать url ссылку на объект.

        Returns:
            str: url ссылку на объект

        """
        obj = self.get_object()
        domain = get_current_site(self.request).domain
        return "".join(
            [
                "https://",
                domain,
                reverse(
                    f"{obj.__class__.__name__.lower()}s-detail",
                    kwargs={"pk": obj.id},
                ),
            ]
        )

    def _get_receiver(self) -> str:
        raise NotImplementedError
