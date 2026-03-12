from django.contrib import admin

from categories.models import Category


@admin.register(Category)
class AdvCategoryAdmin(admin.ModelAdmin):
    """Отображение модели категорий в админке."""

    list_display = ["id", "title"]  # noqa: RUF012
    search_fields = ["title"]  # noqa: RUF012
    list_filter = ["parent"]  # noqa: RUF012
