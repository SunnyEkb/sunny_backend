from factory import (
    Faker,
    fuzzy,
    Sequence,
    SubFactory,
)
from factory.django import DjangoModelFactory

from core.choices import ServicePlace
from core.enums import Limits
from services.models import Service, Type
from users.tests.factories import CustomUserFactory


class TypeFactory(DjangoModelFactory):
    """Фабрика для создания экзмпляров модели тип услуги."""

    class Meta:
        model = Type

    title = Faker("name")


class ServiceFactory(DjangoModelFactory):
    """Фабрика для экземпляров модели услуг."""

    class Meta:
        model = Service

    provider = SubFactory(CustomUserFactory)
    title = Sequence(lambda o: "service_{0}".format(o))
    experience = fuzzy.FuzzyInteger(0, 25)
    place_of_provision = fuzzy.FuzzyChoice(ServicePlace.choices)
    description = fuzzy.FuzzyText(
        length=Limits.MAX_LENGTH_ADVMNT_DESCRIPTION.value
    )
    salon_name = fuzzy.FuzzyText(
        length=Limits.MAX_LENGTH_SERVICE_SALON_NAME.value
    )
    address = fuzzy.FuzzyText(length=Limits.MAX_LENGTH_SERVICE_ADDRESS.value)
