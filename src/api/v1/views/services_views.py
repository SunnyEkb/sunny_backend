import sys

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import (
    exceptions,
    mixins,
    viewsets,
    permissions,
    response,
    status,
)
from rest_framework.decorators import action

from api.v1.filters import ServiceFilter
from api.v1.paginators import CustomPaginator
from api.v1.permissions import (
    OwnerOrReadOnly,
    PhotoOwnerOrReadOnly,
    ReadOnly,
    PhotoReadOnly,
)
from api.v1 import schemes
from api.v1 import serializers as api_serializers
from core.choices import AdvertisementStatus, APIResponses
from core.utils import notify_about_moderation
from services.models import Service, ServiceImage, Type
from users.models import Favorites

User = get_user_model()


@extend_schema(
    tags=["Services types"],
    examples=[schemes.TYPE_LIST_FLAT_EXAMPLE],
    responses={
        status.HTTP_200_OK: schemes.TYPES_GET_OK_200,
    },
    parameters=[
        OpenApiParameter("title", str),
        OpenApiParameter("id", int),
    ],
)
@extend_schema_view(
    list=extend_schema(summary="Список типов услуг."),
)
class TypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Список типов услуг."""

    def get_queryset(self):
        params = self.request.query_params
        if "title" in params:
            title = params.get("title")
            queryset = Type.objects.filter(title__icontains=title)
        elif "id" in params:
            try:
                type_id = int(params.get("id"))
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
            queryset = Type.objects.filter(id=type_id)
        else:
            queryset = Type.objects.filter(parent=None)
        return queryset

    def get_serializer_class(self):
        params = self.request.query_params
        if "title" in params:
            return api_serializers.TypeGetWithoutSubCatSerializer
        return api_serializers.TypeGetSerializer

    @method_decorator(cache_page(60 * 2))
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except exceptions.ValidationError:
            return response.Response(
                data={"detail": APIResponses.INVALID_PARAMETR.value},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(
    tags=["Services"],
)
@extend_schema_view(
    list=extend_schema(
        summary=(
            "Список услуг. Для получения списка услуг по категориям необходимо"
            " указать query параметр 'type_id'."
        ),
        parameters=[OpenApiParameter("type_id", int)],
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
            status.HTTP_400_BAD_REQUEST: schemes.WRONG_PARAMETR_400,
        },
    ),
    retrieve=extend_schema(
        summary="Информация о конкретной услуге.",
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
    create=extend_schema(
        request=api_serializers.ServiceCreateUpdateSerializer,
        summary="Создание услуги.",
        responses={
            status.HTTP_201_CREATED: schemes.SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
        },
        examples=[schemes.SERVICE_CREATE_UPDATE_EXAMPLE],
    ),
    update=extend_schema(
        request=api_serializers.ServiceCreateUpdateSerializer,
        summary="Изменение данных услуги.",
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
        examples=[schemes.SERVICE_CREATE_UPDATE_EXAMPLE],
    ),
    partial_update=extend_schema(
        request=api_serializers.ServiceCreateUpdateSerializer,
        summary="Изменение данных услуги.",
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
        examples=[schemes.SERVICE_PARTIAL_UPDATE_EXAMPLE],
    ),
    destroy=extend_schema(
        summary="Удалить услугу.",
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: schemes.CANT_DELETE_SERVICE_406,
        },
    ),
)
class ServiceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Операции с услугами."""

    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ServiceFilter

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

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return api_serializers.ServiceListSerializer
        return api_serializers.ServiceCreateUpdateSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return (ReadOnly(),)
        if self.action in ["add_to_favorites", "delete_from_favorites"]:
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
        instance: Service = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        # смена статуса на CHANGED для повторной модерации
        instance.set_changed()
        return response.Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance: Service = self.get_object()
        if instance.status == AdvertisementStatus.DRAFT:
            instance.delete_images()
            return super().destroy(request, *args, **kwargs)
        return response.Response(
            APIResponses.CAN_NOT_DELETE_SEVICE.value,
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )

    @extend_schema(
        summary="Отменить услугу.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: (
                schemes.CANT_CANCELL_SERVICE_OR_AD_406
            ),
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="cancell",
        url_name="cancell",
        permission_classes=(OwnerOrReadOnly,),
    )
    def cancell(self, request, *args, **kwargs):
        """Отменить услугу."""

        service: Service = self.get_object()
        if service.status == AdvertisementStatus.DRAFT.value:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.CAN_NOT_CANCELL_SERVICE_OR_AD.value,
            )
        service.cancell()
        serializer = self.get_serializer(service)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Скрыть услугу.",
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
        permission_classes=(OwnerOrReadOnly,),
    )
    def hide(self, request, *args, **kwargs):
        """Скрыть услугу."""

        service: Service = self.get_object()
        if not service.status == AdvertisementStatus.PUBLISHED.value:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.CAN_NOT_HIDE_SERVICE_OR_AD.value,
            )
        service.hide()
        serializer = self.get_serializer(service)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Отправить на модерацию.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: schemes.CANT_MODERATE_SERVICE_406,
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="moderate",
        url_name="moderate",
        permission_classes=(OwnerOrReadOnly,),
    )
    def moderate(self, request, *args, **kwargs):
        """Отправить на модерацию."""

        service: Service = self.get_object()
        if service.status == AdvertisementStatus.CANCELLED.value:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.AD_OR_SERVICE_IS_CANCELLED.value,
            )
        service.send_to_moderation()
        if "test" not in sys.argv:
            notify_about_moderation(service.get_admin_url(request))
        serializer = self.get_serializer(service)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Опубликовать скрытую услугу.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
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
    def publish_hidden_service(self, request, *args, **kwargs):
        """Опубликовать скрытую услугу."""

        service: Service = self.get_object()
        if not service.status == AdvertisementStatus.HIDDEN.value:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.SERVICE_OR_AD_IS_NOT_HIDDEN.value,
            )
        service.publish()
        serializer = self.get_serializer(service)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Добавить фото к услуге.",
        methods=["POST"],
        request=api_serializers.ServiceImageCreateSerializer,
        responses={
            status.HTTP_200_OK: schemes.SERVICE_LIST_OK_200,
            status.HTTP_400_BAD_REQUEST: schemes.CANT_ADD_PHOTO_400,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: schemes.CANT_ADD_PHOTO_406,
        },
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

        service: Service = self.get_object()
        data = request.data
        img_serializer = api_serializers.ServiceImageCreateSerializer(
            data=data
        )
        images = service.images.all()
        if len(images) >= 5:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.MAX_IMAGE_QUANTITY_EXEED.value,
            )
        if img_serializer.is_valid():
            img_serializer.save(service=service)
            srvc_serializer = api_serializers.ServiceListSerializer(service)
            return response.Response(srvc_serializer.data)
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

        service: Service = self.get_object()
        if service.status != AdvertisementStatus.PUBLISHED.value:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_IS_NOT_PUBLISHED.value,
            )
        if Favorites.objects.filter(
            content_type=ContentType.objects.get(
                app_label="services", model="service"
            ),
            object_id=service.id,
            user=request.user,
        ).exists():
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_ALREADY_IN_FAVORITES.value,
            )
        if service.provider == request.user:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_PROVIDER_CANT_ADD_TO_FAVORITE.value,
            )
        Favorites.objects.create(
            content_type=ContentType.objects.get(
                app_label="services", model="service"
            ),
            object_id=service.id,
            user=request.user,
        )
        return response.Response(
            status=status.HTTP_201_CREATED,
            data=APIResponses.ADDED_TO_FAVORITES.value,
        )

    @extend_schema(
        summary="Удалить из избранного.",
        methods=["POST"],
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

        service: Service = self.get_object()
        if not Favorites.objects.filter(
            content_type=ContentType.objects.get(
                app_label="services", model="service"
            ),
            object_id=service.id,
            user=request.user,
        ).exists():
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_NOT_IN_FAVORITES.value,
            )
        Favorites.objects.get(
            content_type=ContentType.objects.get(
                app_label="services", model="service"
            ),
            object_id=service.id,
            user=request.user,
        ).delete()
        return response.Response(
            status=status.HTTP_204_NO_CONTENT,
            data=APIResponses.DELETED_FROM_FAVORITES.value,
        )


@extend_schema(
    tags=["Services"],
    responses={
        status.HTTP_204_NO_CONTENT: None,
    },
)
@extend_schema_view(
    destroy=extend_schema(summary="Удаление фото."),
    retrieve=extend_schema(summary="Получение фото."),
    responses={
        status.HTTP_204_NO_CONTENT: None,
        status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
    },
)
class ServiceImageViewSet(
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Фото к услугам."""

    queryset = ServiceImage.objects.all()
    serializer_class = api_serializers.ServiceImageRetrieveSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return (PhotoReadOnly(),)
        return (PhotoOwnerOrReadOnly(),)

    def destroy(self, request, *args, **kwargs):
        instance: ServiceImage = self.get_object()

        # удаляем файл
        if "test" not in sys.argv:
            instance.delete_image_files()

        return super().destroy(request, *args, **kwargs)
