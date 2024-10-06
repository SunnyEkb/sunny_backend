from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import UserChangeForm, UserCreationForm
from users.models import CustomUser, Favorites


@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    """
    Отображение модели пользователя в админке.
    """

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_active",
        "role",
        "date_joined",
    ]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Персональная информация", {"fields": ["first_name", "last_name"]}),
        ("Разрешения", {"fields": ["is_active", "role", "is_staff"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "password1", "password2"],
            },
        ),
    ]
    list_filter = ["role", "is_active"]
    search_fields = ["email"]
    ordering = ["email"]


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    """
    Отображение модели избранное в админке.
    """

    list_display = [
        "user",
        "content_type",
        "object_id",
    ]
    list_filter = ["content_type"]
    search_fields = ["user", "object_id"]
