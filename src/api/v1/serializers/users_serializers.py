from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.serializers import (
    CharField,
    EmailField,
    ListField,
    ModelSerializer,
    Serializer,
    ValidationError,
)
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from api.v1.serializers.image_fields import Base64ImageField
from api.v1.validators import (
    validate_email,
    validate_email_length,
    validate_file_size,
    validate_phone,
    validate_username,
)
from core.choices import APIResponses
from users.models import VerificationToken

User = get_user_model()

if TYPE_CHECKING:
    from django.db.models import Model

    from users.models import CustomUser


class UserReadSerializer(ModelSerializer):
    """Сериализатор для получения данных о пользователе."""

    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        """Настройки сериализатора для получения данных о пользователе."""

        model = User
        fields = (
            "id",
            "username",
            "email",
            "phone",
            "first_name",
            "last_name",
            "role",
            "avatar",
        )


class UserSearchSerializer(ModelSerializer):
    """Сериализатор для получения данных о пользователе."""

    class Meta:
        """Настройки сериализатора для получения данных о пользователе."""

        model = User
        fields = ("id", "email")


class UserCreateSerializer(ModelSerializer):
    """Сериализатор для создания пользователя."""

    phone = PhoneNumberField(required=True, region="RU", validators=[validate_phone])
    confirmation = CharField(write_only=True, required=True)
    username = CharField(required=True, validators=[validate_username])
    email = EmailField(validators=[validate_email, validate_email_length])

    class Meta:
        """Настройка сериализатор для создания пользователя."""

        model = User
        fields = (
            "username",
            "email",
            "phone",
            "password",
            "confirmation",
        )
        extra_kwargs = {"password": {"write_only": True}}  # noqa: RUF012

    def validate(self, attrs: dict) -> dict:
        """Валидация данных.

        Args:
            attrs (dict): данные

        Returns:
            dict: проверенные данные

        """
        if attrs["password"] != attrs["confirmation"]:
            raise ValidationError(APIResponses.PASSWORD_DO_NOT_MATCH)

        data = attrs.copy()
        del data["confirmation"]

        errors = {}
        user = User(**data)

        try:
            password_validation.validate_password(password=attrs["password"], user=user)
        except ValidationError as e:
            errors["password"] = list(e.messages)

        if errors:
            raise ValidationError(errors)
        return attrs

    def create(self, validated_data: dict) -> "CustomUser":
        """Создать пользователя.

        Args:
            validated_data (dict): данные

        Returns:
            CustomUser: созданный пользователь

        """
        _ = validated_data.pop("confirmation")
        return User.objects.create_user(**validated_data)

    def to_representation(self, instance: "Model") -> dict:
        """Представить данные.

        Args:
            instance (Model): данные

        Returns:
            dict: данные в изменененном виде

        """
        serializer = UserReadSerializer(instance)
        return serializer.data


class UserUpdateSerializer(ModelSerializer):
    """Сериализатор для изменения данных о пользователе."""

    phone = PhoneNumberField(region="RU")

    class Meta:
        """Настройки сериализатора для изменения данных о пользователе."""

        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "phone",
        )

    def to_representation(self, instance: "Model") -> dict:
        """Представить данные.

        Args:
            instance (Model): данные

        Returns:
            dict: данные в изменененном виде

        """
        serializer = UserReadSerializer(instance)
        return serializer.data


class UserAdAvatarSerializer(ModelSerializer):
    """Сериализатор для изменения фото пользователя."""

    avatar = Base64ImageField(
        required=True,
        allow_null=True,
        validators=[validate_file_size],
    )

    class Meta:
        """Настройки сериализатора для изменения фото пользователя."""

        model = User
        fields = ("avatar",)

    def to_representation(self, instance: "Model") -> dict:
        """Представить данные.

        Args:
            instance (Model): данные

        Returns:
            dict: данные в изменененном виде

        """
        serializer = UserReadSerializer(instance)
        return serializer.data


class NonErrorFieldSerializer(Serializer):
    """Сериализатор для ошибок валидации вводимых данных."""

    non_error_field = ListField(read_only=True)


class LoginSerializer(Serializer):
    """Сериализатор для входа в систему."""

    email = EmailField(write_only=True, required=True)
    password = CharField(write_only=True, required=True)


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    """Сериализатор для обновления refresh токена вайлах cookie."""

    refresh = None

    def validate(self, attrs: dict) -> dict:
        """Валидация данных.

        Args:
            attrs (dict): данные

        Returns:
            dict: проверенные данные

        """
        attrs["refresh"] = self.context["request"].COOKIES.get(
            settings.SIMPLE_JWT["AUTH_REFRESH"]
        )
        if attrs["refresh"]:
            return super().validate(attrs)
        raise InvalidToken(APIResponses.INVALID_TOKEN)


class PasswordChangeSerializer(Serializer):
    """Сериализатор для смены пароля."""

    current_password = CharField(required=True)
    new_password = CharField(required=True)
    confirmation = CharField(required=True)

    def validate(self, attrs: dict) -> dict:
        """Валидация данных.

        Args:
            attrs (dict): данные

        Returns:
            dict: проверенные данные

        """
        user = self.initial_data["user"]
        if not user.check_password(attrs["current_password"]):
            raise ValidationError({"password": APIResponses.WRONG_PASSWORD})
        if (
            not self.initial_data["new_password"].strip()
            == self.initial_data["confirmation"].strip()
        ):
            raise ValidationError({"password": APIResponses.PASSWORD_DO_NOT_MATCH})
        if (
            self.initial_data["new_password"].strip()
            == self.initial_data["current_password"]
        ):
            raise ValidationError({"password": APIResponses.NOT_SAME_PASSWORD})

        errors = {}
        try:
            password_validation.validate_password(
                password=attrs["new_password"], user=user
            )
        except ValidationError as e:
            errors["password"] = list(e.messages)

        if errors:
            raise ValidationError(errors)
        return attrs


class VerificationTokenSerialiser(ModelSerializer):
    """Сериализатор для подтверждения регистрации."""

    class Meta:
        """Настройки сериализатора для подтверждения регистрации."""

        model = VerificationToken
        fields = ("token",)
