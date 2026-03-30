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
            subcat = []
            for subcategory in obj.subcategories.all():
                subcat.append(CategorySerializer(subcategory).data)
            return subcat
        return None


class CommonCategoryNoSubCatSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка категорий без подкатегорий."""

    class Meta:
        """Настройки сериализатора."""

        model = Category
        fields = ("id", "title", "image")
