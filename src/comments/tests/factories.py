from factory import fuzzy, SubFactory
from factory.django import DjangoModelFactory

from comments.models import Comment
from core.enums import Limits
from users.tests.factories import CustomUserFactory


class CommentFactory(DjangoModelFactory):
    """Фабрика для создания экзмпляров модели комментария."""

    class Meta:
        model = Comment

    author = SubFactory(CustomUserFactory)
    rating = fuzzy.FuzzyInteger(1, 5)
    feedback = fuzzy.FuzzyText(length=Limits.MAX_COMMENT_TEXT.value)
