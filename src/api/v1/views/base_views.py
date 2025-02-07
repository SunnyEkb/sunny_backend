import abc

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema
from rest_framework import (
    exceptions,
    mixins,
    views,
    viewsets,
    pagination,
    permissions,
    response,
    status,
)
from rest_framework.decorators import action
from ads.models import Ad
from api.v1.paginators import CustomPaginator
from api.v1.permissions import OwnerOrReadOnly, ReadOnly
from api.v1 import schemes
from api.v1 import serializers as api_serializers
from config.settings.base import ALLOWED_IMAGE_FILE_EXTENTIONS
from comments.models import Comment
from core.choices import AdvertisementStatus, APIResponses
from services.models import Service
from bad_word_filter.tasks import moderate_comment
from users.models import Favorites


class BaseServiceAdViewSet(
    mixins.ListModelMixin,
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

    def get_queryset(self):
        queryset = Service.cstm_mng.all()
        if self.action == "list":
            params = self.request.query_params
            queryset = queryset.filter(
                status=AdvertisementStatus.PUBLISHED.value
            )
            if "type_id" in params:
                try:
                    type_id = int(params.get("type_id"))
                except ValueError:
                    raise exceptions.ValidationError(
                        detail=APIResponses.INVALID_PARAMETR.value,
                        code=status.HTTP_400_BAD_REQUEST,
                    )
                if type_id < 0:
                    raise exceptions.ValidationError(
                        detail=APIResponses.INVALID_PARAMETR.value,
                        code=status.HTTP_400_BAD_REQUEST,
                    )
                queryset = queryset.filter(type__id=type_id)
        return queryset

    def get_permissions(self):
        if self.action == "retrieve":
            return (ReadOnly(),)
        if self.action in [
            "add_to_favorites",
            "delete_from_favorites",
            "add_comment",
        ]:
            return (permissions.IsAuthenticated(),)
        return (OwnerOrReadOnly(),)

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except exceptions.ValidationError:
            return response.Response(
                data={"detail": APIResponses.INVALID_PARAMETR.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        # смена статуса на DRAFT для повторной модерации
        instance.set_draft()
        return response.Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
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
            status.HTTP_406_NOT_ACCEPTABLE: (
                schemes.CANT_HIDE_SERVICE_OR_AD_406
            ),
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="hide",
        url_name="hide",
        permission_classes=(OwnerOrReadOnly,),
    )
    def hide(self, request, *args, **kwargs):
        """Скрыть услугу или объявление."""

        object = self.get_object()
        if not object.status == AdvertisementStatus.PUBLISHED.value:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.CAN_NOT_HIDE_SERVICE_OR_AD.value,
            )
        object.hide()
        serializer = self.get_serializer(object)
        return response.Response(serializer.data)

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
            status.HTTP_406_NOT_ACCEPTABLE: (
                schemes.CANT_PUBLISH_SERVICE_OR_AD_406
            ),
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="publish",
        url_name="publish",
        permission_classes=(OwnerOrReadOnly,),
    )
    def publish_object(self, request, *args, **kwargs):
        """Опубликовать услугу или объявление."""

        object = self.get_object()
        obj_status = object.status
        if obj_status not in [
            AdvertisementStatus.DRAFT.value,
            AdvertisementStatus.HIDDEN.value,
        ]:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.SERVICE_OR_AD_CANT_BE_PUBLISHED.value,
            )
        object.publish(request)
        if obj_status == AdvertisementStatus.HIDDEN.value:
            serializer = self.get_serializer(object)
            return response.Response(serializer.data)
        return response.Response(
            APIResponses.AD_OR_SERVICE_SENT_MODERATION.value
        )

    @extend_schema(
        summary="Добавить фото к услуге.",
        methods=["POST"],
        request=api_serializers.AdImageCreateSerializer,
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
    def add_photo(self, request, *args, **kwargs):
        """Добавить фото к услуге."""

        object: Service = self.get_object()

        # Проверяем, чтобы количество фото было не больше максимума
        images = object.images.all()
        if len(images) >= 5:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.MAX_IMAGE_QUANTITY_EXEED.value,
            )

        data = request.data
        # Определяем необходимый сериализатор
        if isinstance(object, Service):
            img_serializer = api_serializers.ServiceImageCreateSerializer(
                data=data
            )
        elif isinstance(object, Ad):
            img_serializer = api_serializers.AdImageCreateSerializer(data=data)

        if img_serializer.is_valid():
            if isinstance(
                img_serializer, api_serializers.ServiceImageCreateSerializer
            ):
                img_serializer.save(service=object)
            else:
                img_serializer.save(ad=object)
            obj_serializer = self.get_serializer(object)
            return response.Response(obj_serializer.data)
        return response.Response(
            img_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Добавить в избранное.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_201_CREATED: schemes.ADDED_TO_FAVORITES_201,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_406_NOT_ACCEPTABLE: (
                schemes.CANT_ADD_TO_FAVORITES_406
            ),
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="add-to-favorites",
        url_name="add_to_favorites",
        permission_classes=(permissions.IsAuthenticated),
    )
    def add_to_favorites(self, request, *args, **kwargs):
        """Добавить в избранное."""

        object = self.get_object()
        if object.status != AdvertisementStatus.PUBLISHED.value:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_IS_NOT_PUBLISHED.value,
            )

        if isinstance(object, Service):
            app_label = "services"
            model = "service"
        else:
            app_label = "ads"
            model = "ad"

        if Favorites.objects.filter(
            content_type=ContentType.objects.get(
                app_label=app_label, model=model
            ),
            object_id=object.id,
            user=request.user,
        ).exists():
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_ALREADY_IN_FAVORITES.value,
            )
        if object.provider == request.user:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_PROVIDER_CANT_ADD_TO_FAVORITE.value,
            )
        Favorites.objects.create(
            content_type=ContentType.objects.get(
                app_label=app_label, model=model
            ),
            object_id=object.id,
            user=request.user,
        )
        return response.Response(
            status=status.HTTP_201_CREATED,
            data=APIResponses.ADDED_TO_FAVORITES.value,
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
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="add-comment",
        url_name="add_comment",
        permission_classes=(permissions.IsAuthenticated),
    )
    def add_comment(self, request, *args, **kwargs):
        """Добавить комментарий."""

        serializer = api_serializers.CommentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return response.Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        object = self.get_object()
        if object.status != AdvertisementStatus.PUBLISHED.value:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_IS_NOT_PUBLISHED.value,
            )

        if isinstance(object, Service):
            app_label = "services"
            model = "service"
        else:
            app_label = "ads"
            model = "ad"

        if Comment.objects.filter(
            content_type=ContentType.objects.get(
                app_label=app_label, model=model
            ),
            object_id=object.id,
            author=request.user,
        ).exists():
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.COMMENT_ALREADY_EXISTS.value,
            )

        if object.provider == request.user:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.COMMENTS_BY_PROVIDER_PROHIBITED.value,
            )

        comment = serializer.save(
            content_type=ContentType.objects.get(
                app_label=app_label, model=model
            ),
            object_id=object.id,
            author=request.user,
        )
        admin_url = comment.get_admin_url(self.request)
        moderate_comment.delay_on_commit(comment.id, admin_url)

        return response.Response(
            status=status.HTTP_201_CREATED,
            data=APIResponses.COMMENT_ADDED.value,
        )

    @extend_schema(
        summary="Удалить из избранного.",
        methods=["DELETE"],
        request=None,
        responses={
            status.HTTP_204_NO_CONTENT: (schemes.DELETED_FROM_FAVORITES_204),
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_406_NOT_ACCEPTABLE: (
                schemes.CANT_DELETE_FROM_FAVORITES_406
            ),
        },
    )
    @action(
        detail=True,
        methods=("delete",),
        url_path="delete-from-favorites",
        url_name="delete_from_favorites",
        permission_classes=(permissions.IsAuthenticated),
    )
    def delete_from_favorites(self, request, *args, **kwargs):
        """Удалить из избранного."""

        object = self.get_object()

        if isinstance(object, Service):
            app_label = "services"
            model = "service"
        else:
            app_label = "ads"
            model = "ad"

        if not Favorites.objects.filter(
            content_type=ContentType.objects.get(
                app_label=app_label, model=model
            ),
            object_id=object.id,
            user=request.user,
        ).exists():
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_NOT_IN_FAVORITES.value,
            )
        Favorites.objects.get(
            content_type=ContentType.objects.get(
                app_label=app_label, model=model
            ),
            object_id=object.id,
            user=request.user,
        ).delete()
        return response.Response(
            status=status.HTTP_204_NO_CONTENT,
            data=APIResponses.DELETED_FROM_FAVORITES.value,
        )


class PaginatedElasticSearchAPIView(
    views.APIView, pagination.LimitOffsetPagination
):
    serializer_class = None
    document_class = None

    @abc.abstractmethod
    def generate_q_expression(self, query):
        """This method should be overridden
        and return a Q() expression."""

    def get(self, request, query):
        try:
            q = self.generate_q_expression(query)
            search = self.document_class.search().query(q)
            response = search.execute()
            results = self.paginate_queryset(response, request, view=self)
            serializer = self.serializer_class(results, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return HttpResponse(e, status=500)


class CategoryTypeViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Базовый вьюсет для типов услуг и объявлений"""

    serializer_class = None

    @method_decorator(cache_page(60 * 2))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 2))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def base_get_queryset(self, queryset):
        if self.action == "list":
            params = self.request.query_params
            if "title" in params:
                title = params.get("title")
                queryset = queryset.filter(title__icontains=title)
            else:
                queryset = queryset.filter(parent=None)
        return queryset
