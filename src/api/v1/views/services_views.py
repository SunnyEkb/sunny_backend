import sys

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, viewsets, permissions, response, status
from rest_framework.decorators import action

from api.v1.filters import ServiceFilter, TypeFilter
from api.v1.paginators import CustomPaginator
from api.v1.permissions import OwnerOrReadOnly, PhotoOwnerOrReadOnly, ReadOnly
from api.v1.schemes import (
    CANT_ADD_PHOTO_400,
    CANT_ADD_PHOTO_406,
    CANT_ADD_SERVICE_TO_FAVORITES_406,
    CANT_DELETE_SERVICE_FROM_FAVORITES_406,
    CANT_CANCELL_SERVICE_406,
    CANT_DELETE_SERVICE_406,
    CANT_HIDE_SERVICE_406,
    CANT_MODERATE_SERVICE_406,
    CANT_PUBLISH_SERVICE_406,
    SERVICE_CREATED_201,
    SERVICE_LIST_OK_200,
    SERVICE_FORBIDDEN_403,
    SERVICE_ADDED_TO_FAVORITES_201,
    SERVICE_DELETED_FROM_FAVORITES_204,
    TYPES_GET_OK_200,
    TYPE_LIST_EXAMPLE,
    UNAUTHORIZED_401,
)
from api.v1.serializers import (
    ServiceImageCreateSerializer,
    ServiceCreateUpdateSerializer,
    ServiceListSerializer,
    TypeGetSerializer,
)
from core.choices import APIResponses, AdvertisementStatus
from core.utils import notify_about_moderation
from services.models import Service, ServiceImage, Type
from users.models import Favorites

User = get_user_model()


@extend_schema(
    tags=["Services types"],
    examples=[TYPE_LIST_EXAMPLE],
    responses={
        status.HTTP_200_OK: TYPES_GET_OK_200,
    },
)
@extend_schema_view(
    list=extend_schema(summary="Список типов услуг."),
)
class TypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Список типов услуг."""

    queryset = Type.objects.filter(parent=None)
    serializer_class = TypeGetSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TypeFilter


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
            status.HTTP_200_OK: SERVICE_LIST_OK_200,
        },
    ),
    retrieve=extend_schema(
        summary="Информация о конкретной услуге.",
        responses={
            status.HTTP_200_OK: SERVICE_LIST_OK_200,
            status.HTTP_403_FORBIDDEN: SERVICE_FORBIDDEN_403,
        },
    ),
    create=extend_schema(
        request=ServiceCreateUpdateSerializer,
        summary="Создание услуги.",
        responses={
            status.HTTP_201_CREATED: SERVICE_CREATED_201,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
        },
    ),
    update=extend_schema(
        request=ServiceCreateUpdateSerializer,
        summary="Изменение данных услуги.",
        responses={
            status.HTTP_200_OK: SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: SERVICE_FORBIDDEN_403,
        },
    ),
    partial_update=extend_schema(
        request=ServiceCreateUpdateSerializer,
        summary="Изменение данных услуги.",
        responses={
            status.HTTP_200_OK: SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: SERVICE_FORBIDDEN_403,
        },
    ),
    destroy=extend_schema(
        summary="Удалить услугу.",
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: SERVICE_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: CANT_DELETE_SERVICE_406,
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
                queryset = queryset.filter(type__id=params.get("type_id"))
        return queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ServiceListSerializer
        return ServiceCreateUpdateSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return (ReadOnly(),)
        if self.action in ["add_to_favorites", "delete_from_favorites"]:
            return (permissions.IsAuthenticated(),)
        return (OwnerOrReadOnly(),)

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)

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

        # смена статуса на CHANGED для повторной модерации
        instance.set_changed()
        return response.Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance: Service = self.get_object()
        if instance.status == AdvertisementStatus.DRAFT:
            instance.delete_service_images()
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
            status.HTTP_200_OK: SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: SERVICE_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: CANT_CANCELL_SERVICE_406,
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
                data=APIResponses.CAN_NOT_CANCELL_SERVICE.value,
            )
        service.cancell()
        serializer = self.get_serializer(service)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Скрыть услугу.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_200_OK: SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: SERVICE_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: CANT_HIDE_SERVICE_406,
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
                data=APIResponses.CAN_NOT_HIDE_SERVICE.value,
            )
        service.hide()
        serializer = self.get_serializer(service)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Отправить на модерацию.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_200_OK: SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: SERVICE_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: CANT_MODERATE_SERVICE_406,
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
                data=APIResponses.SERVICE_IS_CANCELLED.value,
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
            status.HTTP_200_OK: SERVICE_LIST_OK_200,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: SERVICE_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: CANT_PUBLISH_SERVICE_406,
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
                data=APIResponses.SERVICE_IS_NOT_HIDDEN.value,
            )
        service.publish()
        serializer = self.get_serializer(service)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Добавить фото к услуге.",
        methods=["POST"],
        request=ServiceImageCreateSerializer,
        responses={
            status.HTTP_200_OK: SERVICE_LIST_OK_200,
            status.HTTP_400_BAD_REQUEST: CANT_ADD_PHOTO_400,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: SERVICE_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: CANT_ADD_PHOTO_406,
        },
    )
    @action(
        detail=True,
        methods=("post",),
        url_path="add_photo",
        url_name="add_photo",
        permission_classes=(OwnerOrReadOnly,),
    )
    def add_photo(self, request, *args, **kwargs):
        """Добавить фото к услуге."""

        service: Service = self.get_object()
        data = request.data
        img_serializer = ServiceImageCreateSerializer(data=data)
        images = service.images.all()
        if len(images) >= 5:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.MAX_IMAGE_QUANTITY_EXEED.value,
            )
        if img_serializer.is_valid():
            img_serializer.save(service=service)
            srvc_serializer = ServiceListSerializer(service)
            return response.Response(srvc_serializer.data)
        return response.Response(
            img_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Добавить в избранное.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_201_CREATED: SERVICE_ADDED_TO_FAVORITES_201,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
            status.HTTP_406_NOT_ACCEPTABLE: CANT_ADD_SERVICE_TO_FAVORITES_406,
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
                data=APIResponses.SERVICE_IS_NOT_PUBLISHED.value,
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
                data=APIResponses.SERVICE_ALREADY_IN_FAVORITES.value,
            )
        if service.provider == request.user:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.SERVICE_PROVIDER_CANT_ADD_TO_FAVORITE.value,
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
            data=APIResponses.SERVICE_ADDED_TO_FAVORITES.value,
        )

    @extend_schema(
        summary="Удалить из избранного.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_204_NO_CONTENT: SERVICE_DELETED_FROM_FAVORITES_204,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
            status.HTTP_406_NOT_ACCEPTABLE: (
                CANT_DELETE_SERVICE_FROM_FAVORITES_406
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
                data=APIResponses.SERVICE_NOT_IN_FAVORITES.value,
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
            data=APIResponses.SERVICE_DELETED_FROM_FAVORITES.value,
        )


@extend_schema(
    tags=["Services"],
    responses={
        status.HTTP_204_NO_CONTENT: None,
    },
)
@extend_schema_view(
    destroy=extend_schema(summary="Удаление фото."),
    responses={
        status.HTTP_204_NO_CONTENT: None,
        status.HTTP_403_FORBIDDEN: SERVICE_FORBIDDEN_403,
    },
)
class ServiceImageViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Фото к услугам."""

    queryset = ServiceImage.objects.all()
    serializer_class = None

    def get_permissions(self):
        if self.action == "retrieve":
            return (ReadOnly(),)
        return (PhotoOwnerOrReadOnly(),)

    def destroy(self, request, *args, **kwargs):
        instance: ServiceImage = self.get_object()

        # удаляем файл
        instance.delete_image_files()

        return super().destroy(request, *args, **kwargs)
