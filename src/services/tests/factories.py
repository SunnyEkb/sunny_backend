from factory import (
    Faker,
    fuzzy,
    Sequence,
    SubFactory,
)
from factory.django import DjangoModelFactory

from core.choices import ServiceCategory, ServicePlace
from core.enums import Limits
from services.models import Service, Type
from users.tests.factories import CustomUserFactory


class TypeFactory(DjangoModelFactory):
    """Фабрика для создания экзмпляров модели тип услуги."""

    class Meta:
        model = Type

    title = Faker("name")
    category = fuzzy.FuzzyChoice(ServiceCategory.choices)


class ServiceFactory(DjangoModelFactory):
    """Фабрика для экземпляров модели услуг."""

    class Meta:
        model = Service

    provider = SubFactory(CustomUserFactory)
    type = SubFactory(TypeFactory)
    title = Sequence(lambda o: "service_{0}".format(o))
    experience = fuzzy.FuzzyInteger(0, 25)
    place_of_provision = fuzzy.FuzzyChoice(ServicePlace.choices)
    description = fuzzy.FuzzyText(
        length=Limits.MAX_LENGTH_ADVMNT_DESCRIPTION.value
    )
