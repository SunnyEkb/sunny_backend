from rest_framework import serializers

from ads.models import Ad, AdCategory, AdImage
from api.v1.validators import validate_file_size


class AdCategorySerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка категорий объявлений."""

    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = AdCategory
        fields = ("id", "title", "subcategories")

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            subcat = []
            for subcategory in obj.subcategories.all():
                subcat.append(AdCategorySerializer(subcategory).data)
            return subcat
        else:
            return None


class AdImageCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания фото к объявлению."""

    image = serializers.ImageField(
        required=True,
        allow_null=False,
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
        fields = (
            "id",
            "image",
        )


class AdCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения объявления."""

    class Meta:
        model = Ad
        fields = (
            "title",
            "description",
            "price",
            "state",
        )


class AdRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра объявления."""

    provider = serializers.StringRelatedField(read_only=True)
    images = AdImageRetrieveSerializer(many=True, read_only=True)

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
            "state",
        )
