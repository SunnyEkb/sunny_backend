from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.v1.serializers import (
    CommentReadSerializer,
    UserReadSerializer,
    UserSearchSerializer,
)
from api.v1.serializers.image_fields import Base64ImageField
from api.v1.validators import (
    validate_base64_field,
    validate_extention,
    validate_file_size,
)
from categories.models import Category
from core.choices import CommentStatus
from services.models import Service, ServiceImage, SubService
from users.models import Favorites


class ServiceImageCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания фото к услуге."""

    image = Base64ImageField(
        required=True,
        allow_null=True,
        validators=[validate_file_size],
    )

    class Meta:
        """Настройки сериализатора."""

        model = ServiceImage
        fields = ("image",)


class ServiceImageRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для получения фото услуг."""

    image = serializers.ImageField(required=True)

    class Meta:
        """Настройки сериализатора."""

        model = ServiceImage
        fields = ("id", "image", "title_photo")


class ServiceImageSerializer(serializers.Serializer):
    """Сериализатор для добавления одного фото к услуге."""

    image = serializers.CharField()

    def validate_image(self, value: str) -> str:
        """Валидация строки в base64.

        Args:
            value (str): строка

        Returns:
            str: строка

        """
        validate_base64_field(value)
        return value


class ServiceImagesSerializer(serializers.Serializer):
    """Сериализатор для добавления нескольких фото к услуге."""

    images = ServiceImageSerializer(many=True)

    def validate_images(self, data: list[str]) -> list[str]:
        """Валидровать изображения.

        Args:
            data (list[str]): изображения в формате base64

        Returns:
            list[str]: изображения в формате base64

        """
        for img in data:
            validate_base64_field(img["image"])
            img_format, _ = img["image"].split(";base64,")
            ext = img_format.split("/")[-1]
            validate_extention(ext)
        return data


class SubServiceSerializer(serializers.ModelSerializer):
    """Сериализатор для подуслуг."""

    class Meta:
        """Настройки сериализатора."""

        model = SubService
        fields = ("id", "title", "price")


class ServiceGetSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для получения списка услуг."""

    provider = UserReadSerializer(read_only=True)
    avg_rating = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    comments_quantity = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    price_list_entries = SubServiceSerializer(many=True, read_only=True)

    class Meta:
        """Настройки сериализатора."""

        model = Service
        fields = (
            "id",
            "type",
            "provider",
            "title",
            "description",
            "experience",
            "place_of_provision",
            "category",
            "status",
            "salon_name",
            "address",
            "avg_rating",
            "comments_quantity",
            "created_at",
            "updated_at",
            "is_favorited",
            "price_list_entries",
        )

    def get_comments_quantity(self, obj: Service) -> int:
        """Получить количество комментариев.

        Args:
            obj (Service): экземпляр услуги

        Returns:
            int: количество комментариев

        """
        return obj.comments.filter(status=CommentStatus.PUBLISHED).count()

    def get_avg_rating(self, obj: Service) -> int | None:
        """Получить средний рейтинг.

        Args:
            obj (Service): экземпляр услуги

        Returns:
            int | None: средний рейтинг

        """
        rating = obj.comments.aggregate(Avg("rating"))
        rating = rating["rating__avg"]
        if rating is None:
            return None
        return round(rating, 1)

    def get_is_favorited(self, obj: Service) -> bool:
        """Определить находится ли услуга в избранном у пользователя.

        Args:
            obj (Service): экземпляр услуги

        Returns:
            bool: услуга в избранном

        """
        request = self.context.get("request", None)
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                return Favorites.objects.filter(
                    user=user,
                    content_type=ContentType.objects.get(
                        app_label="services", model="service"
                    ),
                    object_id=obj.id,
                ).exists()
        return False

    def get_type(self, obj: Service) -> str:  # noqa: ARG002
        """Получить тип услуги.

        Args:
            obj (Service): экземпляр услуги

        Returns:
            str: тип услуги

        """
        return self.Meta.model.__name__.lower()


class ServiceListSerializer(ServiceGetSerializer):
    """Сериализатор для получения списка услуг."""

    title_photo = serializers.SerializerMethodField()

    class Meta(ServiceGetSerializer.Meta):
        """Настройки сериализатора."""

        fields = ServiceGetSerializer.Meta.fields + ("title_photo",)  # type: ignore  # noqa: PGH003, RUF005

    def get_title_photo(self, obj: Service) -> dict | None:
        title_photo = obj.images.filter(title_photo=True).first()
        if title_photo:
            return ServiceImageRetrieveSerializer(title_photo).data
        return None


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения услуги."""

    category_id = serializers.IntegerField(write_only=True)
    price_list_entries = SubServiceSerializer(many=True, required=False)

    class Meta:
        """Настройки сериализатора."""

        model = Service
        fields = (
            "title",
            "description",
            "experience",
            "place_of_provision",
            "category_id",
            "category",
            "salon_name",
            "address",
            "price_list_entries",
        )
        read_only_fields = ("category",)

    def create(self, validated_data: dict) -> Service:
        """Cоздать услугу.

        Args:
            validated_data (dict): исходные данные

        Returns:
            Service: Созданная услуга

        """
        with transaction.atomic():
            category = get_object_or_404(Category, pk=validated_data.pop("category_id"))
            price_list_entries_data = validated_data.pop("price_list_entries", [])
            main_service = Service.objects.create(**validated_data)
            self.__ad_category(main_service, category)
            if price_list_entries_data:
                self.__add_price_list_entries(main_service, price_list_entries_data)

        return main_service

    def update(self, instance: Service, validated_data: dict) -> Service:
        """Изменить услугу.

        Args:
            instance (Service): экземпляр услуги
            validated_data (dict): данные услуги

        Returns:
            Service: измененная услуга

        """
        with transaction.atomic():
            if "category_id" in validated_data:
                category = get_object_or_404(
                    Category, pk=validated_data.pop("category_id")
                )
                if category not in instance.category.all():
                    categories = instance.category.all()
                    for t in categories:
                        instance.categories.remove(t)
                    self.__ad_category(instance, category)

            if "price_list_entries" in validated_data:
                instance = self.__update_price_list_entries(
                    instance, validated_data.pop("price_list_entries", [])
                )

            return super().update(instance, validated_data)

    def __ad_category(self, service: Service, category: Category) -> None:
        service.category.add(category)
        if category.parent:
            self.__ad_category(service, category.parent)

    def __add_price_list_entries(
        self, instance: Service, price_list_entries_data: list[dict]
    ) -> None:
        """Создание записей прайс-листа."""
        sub_services = [
            SubService(main_service=instance, **data)
            for data in price_list_entries_data
        ]
        SubService.objects.bulk_create(sub_services)

    def __update_price_list_entries(
        self, instance: Service, price_list_entries_data: list[dict]
    ) -> Service:
        """Обновление записей прайс-листа."""
        instance.price_list_entries.all().delete()
        self.__add_price_list_entries(instance, price_list_entries_data)
        return instance

    def to_representation(self, instance: Service) -> dict:
        """Представить данные.

        Args:
            instance (Service): данные

        Returns:
            dict: данные в изменененном виде

        """
        serializer = ServiceListSerializer(instance)
        return serializer.data


class ServiceRetrieveSerializer(ServiceGetSerializer):
    """Сериализатор для получения данных о конкретной услуге."""

    comments = serializers.SerializerMethodField()
    images = ServiceImageRetrieveSerializer(many=True, read_only=True)

    class Meta(ServiceGetSerializer.Meta):
        """Настройки сериализатора."""

        fields = ServiceGetSerializer.Meta.fields + ("comments", "images")  # type: ignore  # noqa: PGH003, RUF005

    def get_comments(self, obj: Service) -> list[CommentReadSerializer]:
        """Вывод трех последних комментариев к услуге."""
        comments = obj.comments.filter(status=CommentStatus.PUBLISHED).order_by(
            "-created_at"
        )[:3]
        return [CommentReadSerializer(comment).data for comment in comments]


class ServiceForModerationSerializer(serializers.ModelSerializer):
    """Сериализатор для модерации услуг."""

    images = ServiceImageRetrieveSerializer(many=True, read_only=True)
    price_list_entries = SubServiceSerializer(many=True, read_only=True)

    class Meta:
        """Настройки сериализатора."""

        model = Service
        fields = (
            "id",
            "title",
            "description",
            "experience",
            "place_of_provision",
            "status",
            "images",
            "salon_name",
            "address",
            "created_at",
            "updated_at",
            "price_list_entries",
        )


class ServiceSearchSerializer(serializers.ModelSerializer):
    """Сериализатор для поиска услуг."""

    provider = UserSearchSerializer(read_only=True)
    type = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        """Настройки сериализатора."""

        model = Service
        fields = (
            "id",
            "type",
            "title",
            "description",
            "address",
            "salon_name",
            "provider",
            "place_of_provision",
            "is_favorited",
        )

    def get_type(self, obj: Service) -> str:  # noqa: ARG002
        """Получить тип объекта.

        Args:
            obj (Service): услуга

        Returns:
            str: тип объекта

        """
        return self.Meta.model.__name__.lower()

    def get_is_favorited(self, obj: Service) -> bool:
        request = self.context.get("request", None)
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                return Favorites.objects.filter(
                    user=user,
                    content_type=ContentType.objects.get(
                        app_label="services", model="service"
                    ),
                    object_id=obj.id,
                ).exists()
        return False
