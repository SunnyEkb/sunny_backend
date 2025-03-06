from rest_framework import serializers

from api.v1.serializers.fields import (
    FavoriteObjectRelatedField,
    SearchObjectRelatedField,
)
from users.models import Favorites


class FavoritesSerialiser(serializers.ModelSerializer):
    """Сериализатор для Избранного."""

    subject = FavoriteObjectRelatedField(read_only=True)

    class Meta:
        model = Favorites
        fields = ["subject"]


class SearchSerialiser(serializers.Serializer):
    """Сериализатор для поиска."""

    subject = SearchObjectRelatedField(read_only=True)
