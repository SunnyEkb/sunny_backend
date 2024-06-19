from rest_framework import serializers

from services.models import Service, ServiceImage, Type


class TypeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения типов услуг."""

    class Meta:
        model = Type
        fields = ("id", "category", "title")


class ServiceImageSerializer(serializers.ModelSerializer):
    """Сериализатор для получения фото услуг."""

    class Meta:
        model = ServiceImage
        fields = ("image",)


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения услуги."""

    images = ServiceImageSerializer(many=True, required=False)
    type = serializers.StringRelatedField()

    class Meta:
        model = Service
        fields = (
            "title",
            "description",
            "experience",
            "place_of_provision",
            "type",
            "price",
        )

    def create(self, validated_data):
        images = validated_data.pop("images")
        service = Service.objects.create(**validated_data)
        for image in images:
            ServiceImage.objects.create(service=service, image=image)
        return service


class ServiceRetreiveSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра услуги."""

    provider = serializers.StringRelatedField(read_only=True)
    images = ServiceImageSerializer(many=True, read_only=True, source="images")
    type = TypeGetSerializer()

    class Meta:
        model = Service
        fields = (
            "id",
            "provider",
            "title",
            "description",
            "experience",
            "place_of_provision",
            "type",
            "price",
            "status",
        )
