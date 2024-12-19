from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
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
from api.v1.validators import validate_file_size
from core.choices import APIResponses
from users.models import VerificationToken

User = get_user_model()


class UserReadSerializer(ModelSerializer):
    """
    Сериализатор для получения данных о пользователе.
    """

    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "first_name",
            "last_name",
            "role",
            "avatar",
        ]


class UserCreateSerializer(ModelSerializer):
    """
    Сериализатор для создания пользователя.
    """

    confirmation = CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "password",
            "confirmation",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["confirmation"]:
            raise ValidationError(APIResponses.PASSWORD_DO_NOT_MATCH.value)

        data = attrs.copy()
        del data["confirmation"]

        errors = dict()
        user = User(**data)

        try:
            password_validation.validate_password(
                password=attrs["password"], user=user
            )
        except ValidationError as e:
            errors["password"] = list(e.messages)

        if errors:
            raise ValidationError(errors)
        return attrs

    def create(self, validated_data):
        _ = validated_data.pop("confirmation")
        user = User.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        serializer = UserReadSerializer(instance)
        return serializer.data


class UserUpdateSerializer(ModelSerializer):
    """
    Сериализатор для изменения данных о пользователе.
    """

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "phone",
        ]

    def to_representation(self, instance):
        serializer = UserReadSerializer(instance)
        return serializer.data


class UserAdAvatarSerializer(ModelSerializer):
    """
    Сериализатор для изменения фото пользователя.
    """

    avatar = Base64ImageField(
        required=True,
        allow_null=True,
        validators=[validate_file_size],
    )

    class Meta:
        model = User
        fields = [
            "avatar",
        ]

    def to_representation(self, instance):
        serializer = UserReadSerializer(instance)
        return serializer.data


class NonErrorFieldSerializer(Serializer):
    """
    Сериализатор для ошибок валидации вводимых данных.
    """

    non_error_field = ListField(read_only=True)


class LoginSerializer(Serializer):
    """Сериализатор для входа в систему."""

    email = EmailField(write_only=True, required=True)
    password = CharField(write_only=True, required=True)


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    """Сериализатор для обновления refresh токена вайлах cookie."""

    refresh = None

    def validate(self, attrs):
        attrs["refresh"] = self.context["request"].COOKIES.get(
            settings.SIMPLE_JWT["AUTH_REFRESH"]
        )
        if attrs["refresh"]:
            return super().validate(attrs)
        else:
            raise InvalidToken(APIResponses.INVALID_TOKEN.value)


class PasswordChangeSerializer(Serializer):
    """
    Сериализатор для смены пароля.
    """

    current_password = CharField(required=True)
    new_password = CharField(required=True)
    confirmation = CharField(required=True)

    def validate(self, attrs):
        user = self.initial_data["user"]
        if not user.check_password(attrs["current_password"]):
            raise ValidationError(
                {"password": APIResponses.WRONG_PASSWORD.value}
            )
        if (
            not self.initial_data["new_password"]
            == self.initial_data["confirmation"]
        ):
            raise ValidationError(
                {"password": APIResponses.PASSWORD_DO_NOT_MATCH.value}
            )
        return attrs


class VerificationTokenSerialiser(ModelSerializer):
    """
    Сериализатор для подтверждения регистрации.
    """

    class Meta:
        model = VerificationToken
        fields = ["token"]
