from rest_framework import serializers

from services.models import Type


class TypeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения типов услуг."""

    class Meta:
        model = Type
        fields = ("category", "title")
