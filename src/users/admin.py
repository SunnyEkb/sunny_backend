from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from users.forms import UserChangeForm, UserCreationForm
from users.models import CustomUser


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
        ("Персональная информация", {"fields": ["first_name", "last_name1"]}),
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
