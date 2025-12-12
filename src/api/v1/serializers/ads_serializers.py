from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from ads.models import Ad, AdImage
from api.v1.serializers.comments_serializers import CommentReadSerializer
from api.v1.serializers.users_serializers import (
    UserReadSerializer,
    UserSearchSerializer,
)
from api.v1.serializers.image_fields import Base64ImageField
from api.v1.validators import (
    validate_base64_field,
    validate_file_size,
    validate_extention,
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
        model = AdImage
        fields = ("image",)


class AdImageSerializer(serializers.Serializer):
    """Сериализатор для добавления одного фото к объявлению."""

    image = serializers.CharField()

    def validate_image(self, value):
        validate_base64_field(value)
        return value


class AdImagesSerializer(serializers.Serializer):
    """Сериализатор для добавления нескольких фото к объявлению."""

    images = AdImageSerializer(many=True)

    def validate_images(self, data):
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
        model = AdImage
        fields = ("id", "image")


class AdListSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра объявления."""

    provider = UserReadSerializer(read_only=True)
    images = AdImageRetrieveSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    comments_quantity = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
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
            "images",
            "condition",
            "category",
            "is_favorited",
            "avg_rating",
            "comments_quantity",
            "created_at",
        )

    def get_is_favorited(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                return Favorites.objects.filter(
                    user=user,
                    content_type=ContentType.objects.get(
                        app_label="ads", model="ad"
                    ),
                    object_id=obj.id,
                ).exists()
        return False

    def get_comments_quantity(self, obj):
        return obj.comments.filter(
            status=CommentStatus.PUBLISHED.value
        ).count()

    def get_avg_rating(self, obj):
        rating = obj.comments.aggregate(Avg("rating"))
        rating = rating["rating__avg"]
        if rating is None:
            return None
        return round(rating, 1)

    def get_type(self, obj):
        return self.Meta.model.__name__.lower()


class AdCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения объявления."""

    category_id = serializers.IntegerField(write_only=True)

    class Meta:
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

    def create(self, validated_data):
        category = get_object_or_404(
            Category, pk=validated_data.pop("category_id")
        )
        ad = Ad.objects.create(**validated_data)
        self.__ad_category(ad, category)
        return ad

    def update(self, instance, validated_data):
        if "category_id" in validated_data:
            category = get_object_or_404(
                Category, pk=validated_data.pop("category_id")
            )
            if category not in instance.category.all():
                categories = instance.category.all()
                for cat in categories:
                    instance.category.remove(cat)
                instance = super().update(instance, validated_data)
                self.__ad_category(instance, category)
        instance = super().update(instance, validated_data)
        return instance

    def __ad_category(self, ad: Ad, category: Category) -> None:
        ad.category.add(category)
        if category.parent:
            self.__ad_category(ad, category.parent)

    def to_representation(self, instance):
        serializer = AdListSerializer(instance)
        return serializer.data


class AdRetrieveSerializer(AdListSerializer):
    """Сериализатор для получения данных о конкретном объявлении."""

    comments = serializers.SerializerMethodField()

    class Meta(AdListSerializer.Meta):
        fields = AdListSerializer.Meta.fields + ("comments",)  # type: ignore  # noqa

    def get_comments(self, obj):
        """Вывод трех последних комментариев к объявлению."""

        comments = obj.comments.filter(
            status=CommentStatus.PUBLISHED
        ).order_by("-created_at")[:3]
        return [CommentReadSerializer(comment).data for comment in comments]


class AdForModerationSerializer(serializers.ModelSerializer):
    """Сериализатор для модерации объявлений."""

    images = AdImageRetrieveSerializer(many=True, read_only=True)

    class Meta:
        model = Ad
        fields = [
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
        ]


class AdSearchSerializer(serializers.ModelSerializer):
    """Сериализатор для посика объявлений."""

    provider = UserSearchSerializer(read_only=True)
    type = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = [
            "id",
            "type",
            "title",
            "address",
            "description",
            "price",
            "provider",
            "condition",
        ]

    def get_type(self, obj):
        return self.Meta.model.__name__.lower()
