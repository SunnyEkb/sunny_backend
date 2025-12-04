from rest_framework import serializers

from categories.models import Category


class CommonCategorySerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка категорий."""

    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "title", "image", "subcategories")

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            subcat = []
            for subcategory in obj.subcategories.all():
                subcat.append(CommonCategorySerializer(subcategory).data)
            return subcat
        else:
            return None


class CommonCategoryNoSubCatSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка категорий без подкатегорий."""

    class Meta:
        model = Category
        fields = ("id", "title", "image")
