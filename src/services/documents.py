from django.contrib.auth import get_user_model
from django.db.models import Model, QuerySet
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from core.choices import ServicePlace
from services.models import Service

User = get_user_model()


@registry.register_document
class ServiceDocument(Document):
    """Документ ElasticSearch для услуг."""

    provider = fields.ObjectField(
        properties={
            "email": fields.TextField(),
            "id": fields.IntegerField(),
        }
    )
    place_of_provision = fields.TextField()

    def prepare_place_of_provision(self, instance: "ServiceDocument") -> str:
        """Преобразовать vесто оказания услуги в строку.

        Returns:
            str: строковое представление места оказания услуги

        """
        if instance.place_of_provision == ServicePlace.HOUSE_CALL:
            return "Выезд"
        if instance.place_of_provision == ServicePlace.OFFICE:
            return "В офисе"
        if instance.place_of_provision == ServicePlace.ON_LINE:
            return "On line"
        return "По выбору"

    class Index:
        """Настройки ElasticSearch."""

        name = "services"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}  # noqa: RUF012

    class Django:
        """Настройки Django."""

        model = Service
        fields = [  # noqa: RUF012
            "id",
            "title",
            "description",
            "address",
            "salon_name",
        ]

        related_models = [User]  # noqa: RUF012

    def get_queryset(self) -> QuerySet:
        """Изменить запрос к БД по умолчанию.

        Returns:
            QuerySet: запрос к БД

        """
        return super().get_queryset().select_related("provider")

    def get_instances_from_related(
        self,
        related_instance: Model,
    ) -> list[Service] | None:
        """Получить список объявлений пользователя.

        Args:
            related_instance (Model): связаная модель

        Returns:
            list[Service] | None: список объявлений пользователя

        """
        if isinstance(related_instance, User):
            return related_instance.services.all()
        return None
