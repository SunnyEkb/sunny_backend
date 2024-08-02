from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.v1.validators import validate_file_size
from services.models import Service, ServiceImage, Type


class TypeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения типов услуг."""

    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Type
        fields = ("id", "title", "subcategories")

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            subcat = []
            for subcategory in obj.subcategories.all():
                subcat.append(TypeGetSerializer(subcategory).data)
            return subcat
        else:
            return None


class ServiceImageCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания фото к услуге."""

    image = serializers.ImageField(
        required=True,
        allow_null=False,
        validators=[validate_file_size],
    )

    class Meta:
        model = ServiceImage
        fields = ("image",)


class ServiceImageRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для получения фото услуг."""

    image = serializers.ImageField(required=True)

    class Meta:
        model = ServiceImage
        fields = (
            "id",
            "image",
        )


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения услуги."""

    type_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Service
        fields = (
            "title",
            "description",
            "experience",
            "place_of_provision",
            "type_id",
            "price",
            "type",
        )
        read_only_fields = ("type",)

    def create(self, validated_data):
        type = get_object_or_404(Type, pk=validated_data.pop("type_id"))
        service = Service.objects.create(**validated_data)
        self.__ad_type(service, type)
        return service

    def update(self, instance, validated_data):
        if "type_id" in validated_data:
            type = get_object_or_404(Type, pk=validated_data.pop("type_id"))
            if type not in instance.type.all():
                types = instance.type.all()
                for t in types:
                    instance.types.remove(t)
                instance = super().update(instance, validated_data)
                self.__ad_type(instance, type)
        instance = super().update(instance, validated_data)
        return instance

    def __ad_type(self, service: Service, type: Type) -> None:
        service.type.add(type)
        if type.parent:
            self.__ad_type(service, type.parent)


class ServiceRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра услуги."""

    provider = serializers.StringRelatedField(read_only=True)
    images = ServiceImageRetrieveSerializer(many=True, read_only=True)

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
            "images",
        )
