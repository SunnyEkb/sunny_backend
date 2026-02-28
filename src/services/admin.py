from django.contrib import admin

from services.models import Service, ServiceImage


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Отображение модели услуг в админке."""

    list_display = [  # noqa: RUF012
        "provider",
        "title",
        "created_at",
        "updated_at",
        "status",
    ]
    search_fields = ["title", "category__title"]  # noqa: RUF012
    list_filter = ["category__title", "status"]  # noqa: RUF012
    ordering = ["-created_at"]  # noqa: RUF012
    readonly_fields = ["created_at"]  # noqa: RUF012


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    """Отображение модели фотографий к услугам в админке."""

    list_display = ["service"]  # noqa: RUF012
    search_fields = ["service__title"]  # noqa: RUF012
