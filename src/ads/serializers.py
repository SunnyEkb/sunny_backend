from django.shortcuts import get_object_or_404
from rest_framework import serializers

from ads.models import Ad, AdImage, Category
from api.v1.validators import validate_file_size


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка категорий объявлений."""

    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "title", "subcategories")

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

    def __ad_category(self, ad: Ad, category: Category) -> None:
        ad.category.add(category)
        if category.parent:
            self.__ad_category(ad, category.parent)


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
            "condition",
            "condition",
            "category",
        )
