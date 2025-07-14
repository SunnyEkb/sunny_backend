from django.contrib.auth import get_user_model
from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from core.choices import ServicePlace
from services.models import Service

User = get_user_model()


@registry.register_document
class ServiceDocument(Document):
    provider = fields.ObjectField(
        properties={
            "email": fields.TextField(),
            "id": fields.IntegerField(),
        }
    )
    place_of_provision = fields.TextField()

    def prepare_place_of_provision(self, instance):
        if instance.place_of_provision == ServicePlace.HOUSE_CALL:
            return "Выезд"
        if instance.place_of_provision == ServicePlace.OFFICE:
            return "В офисе"
        if instance.place_of_provision == ServicePlace.ON_LINE:
            return "On line"
        return "По выбору"

    class Index:
        name = "services"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Service
        fields = [
            "id",
            "title",
            "description",
            "address",
            "salon_name",
        ]

        related_models = [User]

    def get_queryset(self):
        return super().get_queryset().select_related("provider")

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.services.all()
