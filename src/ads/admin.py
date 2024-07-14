from django.contrib import admin

from ads.models import Ad, AdImage


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """Отображение модели объявлений в админке."""

    list_display = [
        "provider",
        "title",
        "category",
        "created_at",
        "updated_at",
        "status",
    ]
    search_fields = ["title", "provider__email"]
    list_filter = ["category", "status"]
    ordering = ["created_at"]


@admin.register(AdImage)
class AdImageAdmin(admin.ModelAdmin):
    """Отображение модели фотографий к объявлениям в админке."""

    list_display = ["ad"]
    search_fields = ["ad__title"]
