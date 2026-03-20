from django.contrib import admin

from comments.models import Comment, CommentImage


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Отображение модели комментариев в админке."""

    list_display = ["author", "created_at", "updated_at"]  # noqa: RUF012
    search_fields = ["author"]  # noqa: RUF012
    ordering = ["created_at"]  # noqa: RUF012


@admin.register(CommentImage)
class ServiceImageAdmin(admin.ModelAdmin):
    """Отображение модели фотографий к комментариям в админке."""

    list_display = ["comment"]  # noqa: RUF012
