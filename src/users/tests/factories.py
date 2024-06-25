from factory import (
    Faker,
    fuzzy,
    PostGenerationMethodCall,
    Sequence,
)
from factory.django import DjangoModelFactory

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
    phone = "+79000" + str(fuzzy.FuzzyInteger(low=100000, high=999999))
    is_active = True
    password = PostGenerationMethodCall("set_password", PASSWORD)
