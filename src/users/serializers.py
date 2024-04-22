from django.contrib.auth import get_user_model
from rest_framework.serializers import (
    CharField,
    ListField,
    ModelSerializer,
    Serializer,
    ValidationError,
)

from core.choices import APIResponses

User = get_user_model()


class UserCreateSerializer(ModelSerializer):
    """
    Сериализатор для создания пользователя.
    """

    confirmation = CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "confirmation",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["confirmation"]:
            raise ValidationError(APIResponses.PASSWORD_DO_NOT_MATCH.value)
        return attrs

    def create(self, validated_data):
        _ = validated_data.pop("confirmation")
        user = User.objects.create_user(**validated_data)
        return user


class UserReadSerializer(ModelSerializer):
    """
    Сериализатор для получения данных о пользователе.
    """

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "role",
        ]


class UserUpdateSerializer(ModelSerializer):
    """
    Сериализатор для изменения данных о пользователе.
    """

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
        ]


class NonErrorFieldSerializer(Serializer):
    """
    Сериализатор для ошибок валидации вводимых данных.
    """

    non_error_field = ListField(read_only=True)
