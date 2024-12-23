from django.contrib.auth import get_user_model
from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from services.models import Service

User = get_user_model()


@registry.register_document
class ServiceDocument(Document):
    title = fields.TextField(
        attr="title",
        fields={
            "suggest": fields.Completion(),
        },
    )
    description = fields.TextField(
        attr="description",
        fields={
            "suggest": fields.Completion(),
        },
    )
    provider = fields.ObjectField(
        properties={
            "email": fields.TextField(),
            "id": fields.IntegerField(),
        }
    )

    class Index:
        name = "services"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Service
        fields = [
            "id",
            "title",
            "description",
        ]

        related_models = [User]

    def get_queryset(self):
        return super().get_queryset().select_related("provider")

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.services.all()
