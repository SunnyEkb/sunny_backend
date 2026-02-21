from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from core.choices import SystemMessages
from users.models import CustomUser


class UserCreationForm(forms.ModelForm):
    """Форма для создания пользователя через админку."""

    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Подтверждение пароля", widget=forms.PasswordInput
    )

    class Meta:
        """Настройки формы."""

        model = CustomUser
        fields = ["email", "username"]

    def clean_password2(self) -> str:
        """Проверить пароль.

        Returns:
            str: пароль, если он валиден

        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(SystemMessages.PASSWORD_DO_NOT_MATCH)
        return password2

    def save(self, commit: bool = True) -> CustomUser:
        """Сохранить пользователя в БД.

        Args:
            commit (bool): зафиксировать изменения в БД.

        Returns:
            CustomUser: Данные сохраненного пользователя.

        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Форма для изменения сведений о пользователе в админке."""

    password = ReadOnlyPasswordHashField()

    class Meta:
        """Настройки Формы."""

        model = CustomUser
        fields = [
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_staff",
        ]
