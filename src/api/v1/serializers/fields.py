from typing import TYPE_CHECKING

from rest_framework import serializers

from ads.documents import AdDocument
from ads.models import Ad
from api.v1.serializers.ads_serializers import (
    AdListSerializer,
    AdSearchSerializer,
)
from api.v1.serializers.services_serializers import (
    ServiceListSerializer,
    ServiceSearchSerializer,
)
from core.exceptions import SerializerNotFoundError
from services.documents import ServiceDocument
from services.models import Service

if TYPE_CHECKING:
    from django.db.models import Model


class FavoriteObjectRelatedField(serializers.RelatedField):
    """Поле для вывода объектов избранного."""

    def to_representation(self, value: "Model") -> dict:
        """Представить данные.

        Args:
            value (Model): данные

        Returns:
            dict: данные в изменененном виде

        """
        if isinstance(value, Service):
            serializer = ServiceListSerializer(value, context=self.context)
        elif isinstance(value, Ad):
            serializer = AdListSerializer(value, context=self.context)
        else:
            raise SerializerNotFoundError
        return serializer.data


class SearchObjectRelatedField(serializers.RelatedField):
    """Поле для вывода результатов поиска."""

    def to_representation(self, value: "Model") -> dict:
        """Представить данные.

        Args:
            value (Model): данные

        Returns:
            dict: данные в изменененном виде

        """
        if isinstance(value, ServiceDocument):
            serializer = ServiceSearchSerializer(value, context=self.context)
        elif isinstance(value, AdDocument):
            serializer = AdSearchSerializer(value, context=self.context)
        else:
            raise SerializerNotFoundError
        return serializer.data
