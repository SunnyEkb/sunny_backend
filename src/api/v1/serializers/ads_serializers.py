from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from ads.models import Ad, AdImage
from api.v1.serializers.comments_serializers import CommentReadSerializer
from api.v1.serializers.image_fields import Base64ImageField
from api.v1.serializers.users_serializers import (
    UserReadSerializer,
    UserSearchSerializer,
)
from api.v1.validators import (
    validate_base64_field,
    validate_extention,
    validate_file_size,
)
from categories.models import Category
from core.choices import CommentStatus
from users.models import Favorites


class AdImageCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления фото к объявлению."""

    image = Base64ImageField(
        required=True,
        allow_null=True,
        validators=[validate_file_size],
    )

    class Meta:
        """Настройки сериализатора для добавления фото к объявлению."""

        model = AdImage
        fields = ("image",)


class AdImageSerializer(serializers.Serializer):
    """Сериализатор для добавления одного фото к объявлению."""

    image = serializers.CharField()

    def validate_image(self, value: str) -> str:
        """Валидация изображения.

        Args:
            str: изображение в base64

        Returns:
            str: изображение в base64

        """
        validate_base64_field(value)
        return value


class AdImagesSerializer(serializers.Serializer):
    """Сериализатор для добавления нескольких фото к объявлению."""

    images = AdImageSerializer(many=True)

    def validate_images(self, data: list[AdImageSerializer]) -> list[AdImageSerializer]:
        """Валидация изображений.

        Args:
            data (list[AdImageSerializer]): список изображений

        Returns:
            list[AdImageSerializer]: список изображений, если он валиден

        """
        for img in data:
            validate_base64_field(img["image"])
            format, _ = img["image"].split(";base64,")
            ext = format.split("/")[-1]
            validate_extention(ext)
        return data


class AdImageRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для получения фото объявлений."""

    image = serializers.ImageField(read_only=True)

    class Meta:
        """Настройки сериализатора для получения фото объявлений."""

        model = AdImage
        fields = ("id", "image", "title_photo")


class AdGetSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для просмотра объявления."""

    provider = UserReadSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    comments_quantity = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        """Настройки сериализатора объявлений."""

        model = Ad
        fields = (
            "id",
            "type",
            "title",
            "description",
            "provider",
            "price",
            "status",
            "address",
            "condition",
            "category",
            "is_favorited",
            "avg_rating",
            "comments_quantity",
            "created_at",
        )

    def get_is_favorited(self, obj: Ad) -> bool:
        """Получить объявление в избранном

        Args:
            obj (Ad): объявление

        Returns:
            bool: объявление в избранном

        """
        request = self.context.get("request", None)
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                return Favorites.objects.filter(
                    user=user,
                    content_type=ContentType.objects.get(app_label="ads", model="ad"),
                    object_id=obj.id,
                ).exists()
        return False

    def get_comments_quantity(self, obj: Ad) -> int:
        """Получить количество комментариев к объявлению.

        Args:
            obj (Ad): объявление

        Returns:
            int: количество комментариев к объявлению

        """
        return obj.comments.filter(status=CommentStatus.PUBLISHED.value).count()  # type: ignore

    def get_avg_rating(self, obj: Ad) -> float | None:
        """Получить средний рейтинг.

        Args:
            obj (Ad): объявление

        Returns:
            float: средний рейтинг объявления

        """
        rating = obj.comments.aggregate(Avg("rating"))
        rating = rating["rating__avg"]
        if rating is None:
            return None
        return round(rating, 1)

    def get_type(self, obj: Ad) -> str:
        """Получить тип объекта.

        Args:
            obj (Ad): объявление

        Returns:
            str: тип объекта

        """
        return self.Meta.model.__name__.lower()


class AdListSerializer(AdGetSerializer):
    """Сериализатор для просмотра объявления."""

    title_photo = serializers.SerializerMethodField()

    class Meta(AdGetSerializer.Meta):
        fields = AdGetSerializer.Meta.fields + ("title_photo",)  # type: ignore

    def get_title_photo(self, obj: Ad) -> dict | None:
        """Получить титульную фотографию.

        Args:
            obj (Ad): объявление

        Returns:
            dict | None: титульная фотография

        """
        title_photo = obj.images.filter(title_photo=True).first()
        if title_photo:
            return AdImageRetrieveSerializer(title_photo).data
        return None


class AdCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения объявления."""

    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        """Настройки сериализатора для создания и изменения объявления."""

        model = Ad
        fields = (
            "title",
            "description",
            "price",
            "address",
            "condition",
            "category_id",
            "category",
        )
        read_only_fields = ("category",)

    def create(self, validated_data: dict) -> Ad:
        """Создать экземпляр объявления.

        Args:
            validated_data (dict): данные объявления, после валидации

        Returns:
            Ad: Созданное объявление

        Raises:
            Http404: Не найдена категория объявления

        """
        category = get_object_or_404(Category, pk=validated_data.pop("category_id"))
        ad = Ad.objects.create(**validated_data)
        self.__ad_category(ad, category)
        return ad

    def update(self, instance: Ad, validated_data: dict) -> Ad:
        """Изменить объявление.

        Args:
            instance (Ad): объявление
            validated_data (dict): данные объявления, после валидации

        Returns:
            Ad: измененное объявление

        Raises:
            Http404: Не найдена категория объявления

        """
        if "category_id" in validated_data:
            category = get_object_or_404(Category, pk=validated_data.pop("category_id"))
            if category not in instance.category.all():
                categories = instance.category.all()
                for cat in categories:
                    instance.category.remove(cat)
                instance = super().update(instance, validated_data)
                self.__ad_category(instance, category)
        instance = super().update(instance, validated_data)
        return instance

    def __ad_category(self, ad: Ad, category: Category) -> None:
        """Добавить категории к объявлению.

        Добавляет родительсткие категории к списку категорий объявления

        Args:
            ad (Ad): объявление
            category (Category): категория, указанная при создании объявления

        """
        ad.category.add(category)
        if category.parent:
            self.__ad_category(ad, category.parent)

    def to_representation(self, instance: Ad) -> dict:
        """Представить данные.

        Args:
            instance (Ad): данные

        Returns:
            dict: данные в изменененном виде

        """
        serializer = AdListSerializer(instance)
        return serializer.data


class AdRetrieveSerializer(AdGetSerializer):
    """Сериализатор для получения данных о конкретном объявлении."""

    comments = serializers.SerializerMethodField()
    images = AdImageRetrieveSerializer(many=True, read_only=True)

    class Meta(AdGetSerializer.Meta):
        """Настройки сериализатора."""

        fields = AdGetSerializer.Meta.fields + ("comments", "images")  # type: ignore  # noqa

    def get_comments(self, obj: Ad) -> list[dict]:
        """Получить три последних комментариев к объявлению.

        Args:
            obj (Ad): экземпляр объявления

        Returns:
            list[dict]: три последних комментариев к объявлению

        """
        comments = obj.comments.filter(status=CommentStatus.PUBLISHED).order_by(
            "-created_at"
        )[:3]
        return [CommentReadSerializer(comment).data for comment in comments]


class AdForModerationSerializer(serializers.ModelSerializer):
    """Сериализатор для модерации объявлений."""

    images = AdImageRetrieveSerializer(many=True, read_only=True)

    class Meta:
        """Настройки сериализатора."""

        model = Ad
        fields = (
            "id",
            "title",
            "description",
            "price",
            "address",
            "status",
            "images",
            "condition",
            "category",
            "created_at",
            "updated_at",
        )


class AdSearchSerializer(serializers.ModelSerializer):
    """Сериализатор для посика объявлений."""

    provider = UserSearchSerializer(read_only=True)
    type = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        """Настройки сериализатора."""

        model = Ad
        fields = (
            "id",
            "type",
            "title",
            "address",
            "description",
            "price",
            "provider",
            "condition",
            "is_favorited",
        )

    def get_type(self, obj: Ad) -> str:  # noqa: ARG002
        """Получить тип объявления.

        Args:
            obj (Ad): экземпляр объявления

        Returns:
            str: тип объявления

        """
        return self.Meta.model.__name__.lower()

    def get_is_favorited(self, obj: Ad) -> bool:
        """Определить находится ли объявление в избранном у пользователя.

        Args:
            obj (Ad): экземпляр объявления

        Returns:
            bool: объявление в избранном

        """
        request = self.context.get("request", None)
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                return Favorites.objects.filter(
                    user=user,
                    content_type=ContentType.objects.get(app_label="ads", model="ad"),
                    object_id=obj.id,
                ).exists()
        return False
