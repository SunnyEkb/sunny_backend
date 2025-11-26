from django.contrib import admin

from categories.models import Category


@admin.register(Category)
class AdvCategoryAdmin(admin.ModelAdmin):
    """Отображение модели категорий в админке."""

    list_display = ["id", "title"]
    search_fields = ["title"]
    list_filter = ["parent"]
