from django.contrib import admin

from ads.models import Ad, AdImage


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """Отображение модели объявлений в админке."""

    list_display = [  # noqa: RUF012
        "provider",
        "title",
        "created_at",
        "updated_at",
        "status",
    ]
    search_fields = ["title", "provider__email"]  # noqa: RUF012
    list_filter = ["status"]  # noqa: RUF012
    ordering = ["-created_at"]  # noqa: RUF012
    readonly_fields = ["created_at"]  # noqa: RUF012


@admin.register(AdImage)
class AdImageAdmin(admin.ModelAdmin):
    """Отображение модели фотографий к объявлениям в админке."""

    list_display = ["ad"]  # noqa: RUF012
    search_fields = ["ad__title"]  # noqa: RUF012
