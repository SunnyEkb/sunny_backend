from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import UserChangeForm, UserCreationForm
from users.models import CustomUser, Favorites, VerificationToken


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Отображение модели пользователя в админке."""

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = [  # noqa: RUF012
        "email",
        "username",
        "first_name",
        "last_name",
        "phone",
        "is_active",
        "role",
        "date_joined",
    ]
    fieldsets = [  # noqa: RUF012
        (None, {"fields": ["email", "password", "phone", "username"]}),
        ("Персональная информация", {"fields": ["first_name", "last_name"]}),
        ("Разрешения", {"fields": ["is_active", "role", "is_staff"]}),
    ]
    add_fieldsets = [  # noqa: RUF012
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "username", "password1", "password2"],
            },
        ),
    ]
    list_filter = ["role", "is_active"]  # noqa: RUF012
    search_fields = ["email"]  # noqa: RUF012
    ordering = ["email"]  # noqa: RUF012


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    """Отображение модели избранное в админке."""

    list_display = ["user", "content_type", "object_id"]  # noqa: RUF012
    list_filter = ["content_type"]  # noqa: RUF012
    search_fields = ["user", "object_id"]  # noqa: RUF012


@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    """Отображение модели токена для подтверждения регистрации в админке."""

    list_display = ["user"]  # noqa: RUF012
    search_fields = ["user__email"]  # noqa: RUF012
    readonly_fields = ["created_at"]  # noqa: RUF012
