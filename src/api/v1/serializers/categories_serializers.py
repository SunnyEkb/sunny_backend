from rest_framework import serializers

from categories.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка категорий."""

    subcategories = serializers.SerializerMethodField()

    class Meta:
        """Настройки сериализатора категорий."""

        model = Category
        fields = ("id", "title", "image", "subcategories")

    def get_subcategories(self, obj: Category) -> None | list[Category]:
        """Получить подкатегории.

        Args:
            obj (Category): категория

        Returns:
            None | list[Category]: Список подкатегорий, если имеются

        """
        if obj.subcategories.exists():
            return [
                CategorySerializer(subcategory).data
                for subcategory in obj.subcategories.all()
            ]
        return None


class CommonCategoryNoSubCatSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка категорий без подкатегорий."""

    class Meta:
        """Настройки сериализатора."""

        model = Category
        fields = ("id", "title", "image")
