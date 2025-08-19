from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from ads.models import Ad, AdImage, Category
from api.v1.serializers.comments_serializers import CommentReadSerializer
from api.v1.serializers.users_serializers import (
    UserReadSerializer,
    UserSearchSerializer,
)
from api.v1.serializers.image_fields import Base64ImageField
from api.v1.validators import validate_file_size
from core.choices import CommentStatus
from users.models import Favorites


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка категорий объявлений."""

    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "title", "image", "subcategories")

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            subcat = []
            for subcategory in obj.subcategories.all():
                subcat.append(CategorySerializer(subcategory).data)
            return subcat
        else:
            return None


class AdImageCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания фото к объявлению."""

    image = Base64ImageField(
        required=True,
        allow_null=True,
        validators=[validate_file_size],
    )

    class Meta:
        model = AdImage
        fields = ("image",)


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
    comments_quantity = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = (
            "id",
            "title",
            "description",
            "provider",
            "price",
            "status",
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


class AdCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения объявления."""

    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Ad
        fields = (
            "title",
            "description",
            "price",
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
    """Сериализатор для получения данных о конкретной услуге."""

    comments = CommentReadSerializer(many=True)

    class Meta(AdListSerializer.Meta):
        fields = AdListSerializer.Meta.fields + ("comments",)  # type: ignore  # noqa


class CategoryGetWithoutSubCatSerializer(serializers.ModelSerializer):
    """Сериализатор для получения категорий объявлений без подкатегорий."""

    class Meta:
        model = Category
        fields = ("id", "title", "image")


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

    class Meta:
        model = Ad
        fields = [
            "id",
            "title",
            "description",
            "price",
            "provider",
            "condition",
        ]
