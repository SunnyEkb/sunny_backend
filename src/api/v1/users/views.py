from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView

from users.serializers import (
    UserCreateSerializer,
)

User = get_user_model()


class RegisrtyView(CreateAPIView):
    """
    Регистрация пользователей.
    """

    def get_queryset(self):
        return User.objects.all()

    serializer_class = UserCreateSerializer
