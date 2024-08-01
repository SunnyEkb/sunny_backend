from django.contrib import admin

from services.models import Service, ServiceImage, Type


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Отображение модели услуг в админке."""

    list_display = [
        "provider",
        "title",
        "created_at",
        "updated_at",
        "status",
    ]
    search_fields = ["title", "type__title"]
    list_filter = ["type__title", "status"]
    ordering = ["created_at"]


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    """Отображение модели фотографий к услугам в админке."""

    list_display = ["service"]
    search_fields = ["service__title"]


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    """Отображение модели типов услуг в админке."""

    list_display = ["id", "title"]
    search_fields = ["title"]
    list_filter = ["parent"]
