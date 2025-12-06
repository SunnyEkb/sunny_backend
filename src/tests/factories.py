from factory import (
    Faker,
    fuzzy,
    PostGenerationMethodCall,
    Sequence,
    SubFactory,
)
from factory.django import DjangoModelFactory

from ads.models import Ad
from categories.models import Category
from core.choices import ServicePlace
from core.enums import Limits
from comments.models import Comment
from notifications.models import Notification
from services.models import Service
from users.models import CustomUser

PASSWORD = "SoMePaSS_word_123"


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = Sequence(lambda n: "user_{}".format(n))
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Sequence(lambda n: "{}@example.org".format(n))
    is_superuser = False
    phone = Sequence(lambda n: "+79{:09}".format(n))
    is_active = True
    password = PostGenerationMethodCall("set_password", PASSWORD)


class CategoryFactory(DjangoModelFactory):
    """Фабрика для создания экзмпляров модели категория."""

    class Meta:
        model = Category

    title = Faker("name")


class AdFactory(DjangoModelFactory):
    """Фабрика для экземпляров модели объявлений."""

    class Meta:
        model = Ad

    provider = SubFactory(CustomUserFactory)
    title = Sequence(lambda o: "ad_{0}".format(o))
    description = fuzzy.FuzzyText(
        length=Limits.MAX_LENGTH_ADVMNT_DESCRIPTION.value
    )
    price = fuzzy.FuzzyDecimal(0, 1000)


class CommentFactory(DjangoModelFactory):
    """Фабрика для создания экзмпляров модели комментария."""

    class Meta:
        model = Comment

    author = SubFactory(CustomUserFactory)
    rating = fuzzy.FuzzyInteger(1, 5)
    feedback = fuzzy.FuzzyText(length=Limits.MAX_COMMENT_TEXT.value)


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


class NotificationFactory(DjangoModelFactory):
    """Фабрика для экземпляров модели уведомлений."""

    class Meta:
        model = Notification

    receiver = SubFactory(CustomUserFactory)
    text = fuzzy.FuzzyText(length=Limits.MAX_LENGTH_NOTIFICATION_TEXT.value)
