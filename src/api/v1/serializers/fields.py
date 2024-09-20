from rest_framework import serializers

from ads.models import Ad
from api.v1.serializers.ads_serializers import AdRetrieveSerializer
from api.v1.serializers.services_serializers import ServiceListSerializer
from core.choices import SystemMessages
from services.models import Service


class FavoriteObjectRelatedField(serializers.RelatedField):
    """
    Поле для вывода объектов избранного.
    """

    def to_representation(self, value):
        if isinstance(value, Service):
            serializer = ServiceListSerializer(value, context=self.context)
        elif isinstance(value, Ad):
            serializer = AdRetrieveSerializer(value, context=self.context)
        else:
            raise Exception(SystemMessages.SERIALIZER_NOT_FOUND_ERROR.value)
        return serializer.data
