from django.contrib.auth import get_user_model
from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from ads.models import Ad
from core.choices import AdState

User = get_user_model()


@registry.register_document
class AdDocument(Document):
    provider = fields.ObjectField(
        properties={
            "email": fields.TextField(),
            "id": fields.IntegerField(),
        }
    )
    condition = fields.TextField()

    def prepare_condition(self, instance):
        if instance.place_of_provision == AdState.USED:
            return "Б/у"
        return "Новый"

    class Index:
        name = "ads"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Ad
        fields = [
            "id",
            "title",
            "description",
            "price",
        ]

        related_models = [User]

    def get_queryset(self):
        return super().get_queryset().select_related("provider")

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.ads.all()
