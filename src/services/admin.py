from django.contrib import admin

from services.models import Service, ServiceImage


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Отображение модели услуг в админке.
    """

    list_display = [
        "provider",
        "title",
        "created_at",
        "updated_at",
    ]
    search_fields = ["title"]
    ordering = ["created_at"]


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    """
    Отображение модели фотографий к услугам в админке.
    """

    list_display = [
        "service",
    ]
    search_fields = ["service__title"]
