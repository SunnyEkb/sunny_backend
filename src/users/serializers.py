from django.contrib.auth import get_user_model
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
)

User = get_user_model()


class UserCreateSerializer(ModelSerializer):
    """
    Сериализатор для создания пользователя.
    """

    password = CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password"
        ]

    def create(self, validated_data):
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
