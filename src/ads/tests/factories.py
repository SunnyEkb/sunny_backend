from factory import (
    Faker,
    fuzzy,
    Sequence,
    SubFactory,
)
from factory.django import DjangoModelFactory

from ads.models import Ad, Category
from core.enums import Limits
from users.tests.factories import CustomUserFactory


class CategoryFactory(DjangoModelFactory):
    """Фабрика для создания экзмпляров модели тип услуги."""

    class Meta:
        model = Category

    title = Faker("name")


class AdFactory(DjangoModelFactory):
    """Фабрика для экземпляров модели объявлений."""

    class Meta:
        model = Ad

    provider = SubFactory(CustomUserFactory)
    title = Sequence(lambda o: "service_{0}".format(o))
    description = fuzzy.FuzzyText(
        length=Limits.MAX_LENGTH_ADVMNT_DESCRIPTION.value
    )
    price = fuzzy.FuzzyDecimal(0, 1000)
