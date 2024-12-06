import sys

from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
)
from rest_framework import mixins, permissions, response, status, viewsets
from rest_framework.decorators import action

from ads.models import Ad, AdImage, Category
from api.v1.paginators import CustomPaginator
from api.v1.permissions import (
    OwnerOrReadOnly,
    ReadOnly,
    PhotoOwnerOrReadOnly,
    PhotoReadOnly,
)
from api.v1 import schemes
from api.v1 import serializers as api_serializers
from core.choices import AdvertisementStatus, APIResponses
from core.utils import notify_about_moderation
from users.models import Favorites


@extend_schema(tags=["Ads categories"])
@extend_schema_view(
    list=extend_schema(
        summary="Список категорий объявлений.",
        responses={status.HTTP_200_OK: schemes.AD_CATEGORIES_GET_OK_200},
    ),
)
class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет для категорий объявлений."""

    queryset = Category.objects.filter(parent=None)
    serializer_class = api_serializers.CategorySerializer

    @method_decorator(cache_page(60 * 2))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(tags=["Ads"])
@extend_schema_view(
    list=extend_schema(
        summary=(
            "Список объявлений. Для получения списка объявлений необходимо"
            " указать query "
            "параметр 'category_id'. При отсутствии параметра"
            " будет выведен пустой список."
        ),
        responses={
            status.HTTP_200_OK: schemes.AD_LIST_OK_200,
        },
        parameters=[OpenApiParameter("category_id", int)],
    ),
    retrieve=extend_schema(
        summary="Информация о конкретном объявлении.",
        responses={
            status.HTTP_200_OK: schemes.AD_RETRIEVE_OK_200,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
    create=extend_schema(
        request=api_serializers.AdCreateUpdateSerializer,
        summary="Создание объявления.",
        examples=[schemes.AD_CREATE_UPDATE_EXAMPLE],
        responses={
            status.HTTP_201_CREATED: schemes.AD_RETRIEVE_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
    update=extend_schema(
        request=api_serializers.AdCreateUpdateSerializer,
        summary="Изменение данных объявления.",
        examples=[schemes.AD_CREATE_UPDATE_EXAMPLE],
        responses={
            status.HTTP_200_OK: schemes.AD_RETRIEVE_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
    partial_update=extend_schema(
        request=api_serializers.AdCreateUpdateSerializer,
        summary="Изменение данных объявления.",
        examples=[schemes.AD_PARTIAL_UPDATE_EXAMPLE],
        responses={
            status.HTTP_200_OK: schemes.AD_RETRIEVE_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
        },
    ),
)
class AdViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для объявлений."""

    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return api_serializers.AdRetrieveSerializer
        return api_serializers.AdCreateUpdateSerializer

    def get_queryset(self):
        queryset = Ad.cstm_mng.all()
        if self.action == "list":
            params = self.request.query_params
            if "category_id" in params:
                queryset = queryset.filter(
                    category__id=params.get("category_id"),
                    status=AdvertisementStatus.PUBLISHED.value,
                )
            else:
                queryset = Ad.objects.none()
        return queryset

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
        instance: Ad = self.get_object()
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

    @extend_schema(
        summary="Отправить на модерацию.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_200_OK: schemes.AD_RETRIEVE_OK_200,
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
        permission_classes=(OwnerOrReadOnly(),),
    )
    def moderate(self, request, *args, **kwargs):
        """Отправить на модерацию."""

        ad: Ad = self.get_object()
        if ad.status == AdvertisementStatus.CANCELLED.value:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.AD_OR_SERVICE_IS_CANCELLED.value,
            )
        ad.send_to_moderation()
        if "test" not in sys.argv:
            notify_about_moderation(ad.get_admin_url(request))
        serializer = self.get_serializer(ad)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Скрыть объявление.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_200_OK: schemes.AD_RETRIEVE_OK_200,
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
        """Скрыть объявление."""

        ad: Ad = self.get_object()
        if not ad.status == AdvertisementStatus.PUBLISHED.value:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.CAN_NOT_HIDE_SERVICE_OR_AD.value,
            )
        ad.hide()
        serializer = self.get_serializer(ad)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Отменить объявление.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_200_OK: schemes.AD_RETRIEVE_OK_200,
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
        """Отменить объявление."""

        ad: Ad = self.get_object()
        if ad.status == AdvertisementStatus.DRAFT.value:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.CAN_NOT_CANCELL_SERVICE_OR_AD.value,
            )
        ad.cancell()
        serializer = self.get_serializer(ad)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Опубликовать скрытое объявление.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_200_OK: schemes.AD_RETRIEVE_OK_200,
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
    def publish_hidden_ad(self, request, *args, **kwargs):
        """Опубликовать скрытое объявление."""

        ad: Ad = self.get_object()
        if not ad.status == AdvertisementStatus.HIDDEN.value:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.SERVICE_OR_AD_IS_NOT_HIDDEN.value,
            )
        ad.publish()
        serializer = self.get_serializer(ad)
        return response.Response(serializer.data)

    @extend_schema(
        summary="Добавить в избранное.",
        methods=["POST"],
        request=None,
        responses={
            status.HTTP_201_CREATED: schemes.ADDED_TO_FAVORITES_201,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_406_NOT_ACCEPTABLE: schemes.CANT_ADD_TO_FAVORITES_406,
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

        ad: Ad = self.get_object()
        if ad.status != AdvertisementStatus.PUBLISHED.value:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_IS_NOT_PUBLISHED.value,
            )
        if Favorites.objects.filter(
            content_type=ContentType.objects.get(app_label="ads", model="ad"),
            object_id=ad.id,
            user=request.user,
        ).exists():
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_ALREADY_IN_FAVORITES.value,
            )
        if ad.provider == request.user:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_PROVIDER_CANT_ADD_TO_FAVORITE.value,
            )
        Favorites.objects.create(
            content_type=ContentType.objects.get(app_label="ads", model="ad"),
            object_id=ad.id,
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
            status.HTTP_204_NO_CONTENT: schemes.DELETED_FROM_FAVORITES_204,
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

        ad: Ad = self.get_object()
        if not Favorites.objects.filter(
            content_type=ContentType.objects.get(app_label="ads", model="ad"),
            object_id=ad.id,
            user=request.user,
        ).exists():
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.OBJECT_NOT_IN_FAVORITES.value,
            )
        Favorites.objects.get(
            content_type=ContentType.objects.get(app_label="ads", model="ad"),
            object_id=ad.id,
            user=request.user,
        ).delete()
        return response.Response(
            status=status.HTTP_204_NO_CONTENT,
            data=APIResponses.DELETED_FROM_FAVORITES.value,
        )

    @extend_schema(
        summary="Добавить фото к объявлению.",
        methods=["POST"],
        request=api_serializers.AdImageCreateSerializer,
        responses={
            status.HTTP_200_OK: schemes.AD_RETRIEVE_OK_200,
            status.HTTP_400_BAD_REQUEST: schemes.CANT_ADD_PHOTO_400,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
            status.HTTP_403_FORBIDDEN: schemes.SERVICE_AD_FORBIDDEN_403,
            status.HTTP_406_NOT_ACCEPTABLE: schemes.CANT_ADD_PHOTO_406,
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
        """Добавить фото к объявлению."""

        ad: Ad = self.get_object()
        data = request.data
        img_serializer = api_serializers.AdImageCreateSerializer(data=data)
        images = ad.images.all()
        if len(images) >= 5:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=APIResponses.MAX_IMAGE_QUANTITY_EXEED.value,
            )
        if img_serializer.is_valid():
            img_serializer.save(ad=ad)
            ad: Ad = self.get_object()
            ad_serializer = api_serializers.AdRetrieveSerializer(ad)
            return response.Response(ad_serializer.data)
        return response.Response(
            img_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    tags=["Ads"],
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
class AdImageViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Фото к объявлениям."""

    queryset = AdImage.objects.all()
    serializer_class = api_serializers.AdImageRetrieveSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return (PhotoReadOnly(),)
        return (PhotoOwnerOrReadOnly(),)

    def destroy(self, request, *args, **kwargs):
        instance: AdImage = self.get_object()

        # удаляем файл
        if "test" not in sys.argv:
            instance.delete_image_files()

        return super().destroy(request, *args, **kwargs)
