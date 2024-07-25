from django.contrib import admin

from ads.models import Ad, AdCategory, AdImage


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """Отображение модели объявлений в админке."""

    list_display = [
        "provider",
        "title",
        "created_at",
        "updated_at",
        "status",
    ]
    search_fields = ["title", "provider__email"]
    list_filter = ["status"]
    ordering = ["-created_at"]


@admin.register(AdImage)
class AdImageAdmin(admin.ModelAdmin):
    """Отображение модели фотографий к объявлениям в админке."""

    list_display = ["ad"]
    search_fields = ["ad__title"]


@admin.register(AdCategory)
class AdvCategoryAdmin(admin.ModelAdmin):
    """Отображение модели категорий к объявлений в админке."""

    list_display = ["id", "title"]
    search_fields = ["title"]
    list_filter = ["parent"]
