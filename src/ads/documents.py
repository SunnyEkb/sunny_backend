from django.contrib.auth import get_user_model
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from ads.models import Ad
from core.choices import AdState

User = get_user_model()


@registry.register_document
class AdDocument(Document):
    """Документ ElasticSearch для объявлений."""

    provider = fields.ObjectField(
        properties={
            "email": fields.TextField(),
            "id": fields.IntegerField(),
        }
    )
    condition = fields.TextField()

    def prepare_condition(self, instance: "AdDocument") -> str:
        """Преобразовать состояние товара в строку.

        Returns:
            str: строковое представление состояния товара

        """
        if instance.condition == AdState.USED:
            return "Б/у"
        return "Новый"

    class Index:
        """Настройки ElasticSearch."""

        name = "ads"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}  # noqa: RUF012

    class Django:
        """Настройки Django."""

        model = Ad
        fields = [  # noqa: RUF012
            "id",
            "title",
            "description",
            "price",
            "address",
        ]

        related_models = [User]  # noqa: RUF012

    def get_queryset(self):
        return super().get_queryset().select_related("provider")

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.ads.all()
