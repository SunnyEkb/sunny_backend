from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.v1.serializers import CommentReadSerializer, UserReadSerializer
from api.v1.serializers.image_fields import Base64ImageField
from api.v1.validators import validate_file_size
from services.models import (
    PriceListEntry,
    Service,
    ServiceImage,
    SubService,
    Type,
)
from users.models import Favorites


class TypeGetWithoutSubCatSerializer(serializers.ModelSerializer):
    """Сериализатор для получения типов услуг без подтипов."""

    class Meta:
        model = Type
        fields = ("id", "title")


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

    image = Base64ImageField(
        required=True,
        allow_null=True,
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
        fields = ("id", "image")


class SubServiceSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подуслуг.
    """

    class Meta:
        model = SubService
        fields = ["id", "title", "price"]


class PriceListEntrySerializer(serializers.ModelSerializer):
    """
    Сериализатор для записи прайс-листа.
    """

    id = serializers.SlugRelatedField(
        source="sub_service",
        slug_field="id",
        queryset=SubService.objects.all(),
    )
    title = serializers.SlugRelatedField(
        source="sub_service", slug_field="title", read_only=True
    )
    price = serializers.SlugRelatedField(
        source="sub_service", slug_field="price", read_only=True
    )

    class Meta:
        model = PriceListEntry
        fields = ["id", "title", "price"]


class ServiceListSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка услуг."""

    provider = UserReadSerializer(read_only=True)
    images = ServiceImageRetrieveSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()
    comments_quantity = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    price_list_entries = PriceListEntrySerializer(many=True, read_only=True)

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
            "salon_name",
            "address",
            "avg_rating",
            "comments_quantity",
            "created_at",
            "updated_at",
            "is_favorited",
            "price_list_entries",
        )

    def get_comments_quantity(self, obj) -> int:
        return obj.comments.count()

    def get_avg_rating(self, obj) -> int:
        rating = obj.comments.aggregate(Avg("rating"))
        rating = rating["rating__avg"]
        if rating is None:
            return None
        return round(rating, 1)

    def get_is_favorited(self, obj) -> bool:
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                return Favorites.objects.filter(
                    user=user,
                    content_type=ContentType.objects.get(
                        app_label="services", model="service"
                    ),
                    object_id=obj.id,
                ).exists()
        return False


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения услуги."""

    type_id = serializers.IntegerField(write_only=True)
    price_list_entries = SubServiceSerializer(many=True, required=False)

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
            "salon_name",
            "address",
            "price_list_entries",
        )
        read_only_fields = ("type",)

    def create(self, validated_data):
        """Метод создания услуги."""

        with transaction.atomic():
            type = get_object_or_404(Type, pk=validated_data.pop("type_id"))
            main_service = Service.objects.create(**validated_data)
            self.__ad_type(main_service, type)
            price_list_entries_data = validated_data.pop(
                "price_list_entries", []
            )
            if price_list_entries_data:
                self.__add_price_list_entries(
                    main_service, price_list_entries_data
                )

        return main_service

    def update(self, instance, validated_data):
        with transaction.atomic():
            if "type_id" in validated_data:
                type = get_object_or_404(
                    Type, pk=validated_data.pop("type_id")
                )
                if type not in instance.type.all():
                    types = instance.type.all()
                    for t in types:
                        instance.types.remove(t)
                    self.__ad_type(instance, type)

            self.__update_price_list_entries(
                instance, validated_data.pop("price_list_entries", [])
            )

            instance = super().update(instance, validated_data)
        return instance

    def __ad_type(self, service: Service, type: Type) -> None:
        service.type.add(type)
        if type.parent:
            self.__ad_type(service, type.parent)

    def __add_price_list_entries(
        self, instance: Service, price_list_entries_data: list[dict]
    ) -> None:
        """
        Метод создания записей для прайс-листа из предварительных данных о
        подуслугах.
        """
        sub_services = [SubService(**data) for data in price_list_entries_data]
        created_sub_services = SubService.objects.bulk_create(sub_services)
        price_list_entries = [
            PriceListEntry(main_service=instance, sub_service=sub_service)
            for sub_service in created_sub_services
        ]
        PriceListEntry.objects.bulk_create(price_list_entries)

    def __update_price_list_entries(
        self, instance: Service, price_list_entries_data: list[dict]
    ) -> Service:
        """Метод обновления записей для прайс-листа и подуслуг."""
        existing_sub_service_ids = [
            entry.sub_service.id for entry in instance.price_list_entries.all()
        ]
        SubService.objects.filter(id__in=existing_sub_service_ids).delete()
        self.__add_price_list_entries(instance, price_list_entries_data)

    def to_representation(self, instance):
        serializer = ServiceListSerializer(instance)
        return serializer.data


class ServiceRetrieveSerializer(ServiceListSerializer):
    """Сериализатор для получения данных о конкретной услуге."""

    comments = CommentReadSerializer(many=True)

    class Meta(ServiceListSerializer.Meta):
        fields = ServiceListSerializer.Meta.fields + ("comments",)
