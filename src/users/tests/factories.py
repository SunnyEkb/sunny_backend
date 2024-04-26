from factory import Faker, fuzzy, LazyAttribute, PostGenerationMethodCall
from factory.django import DjangoModelFactory

from users.models import CustomUser

PASSWORD = "SoMePaSS_word_123"


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = LazyAttribute(lambda o: f"{o.last_name}@example.org")
    is_superuser = False
    phone = "+79000" + str(fuzzy.FuzzyInteger(low=100000, high=999999))
    is_active = True
    password = PostGenerationMethodCall("set_password", PASSWORD)
