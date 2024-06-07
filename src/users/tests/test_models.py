from rest_framework.test import APITestCase

from core.choices import Notifications, Role
from notifications.models import Notification
from users.models import CustomUser
from users.tests.factories import CustomUserFactory


class UsersModelsTest(APITestCase):
    """Класс для тестирования моделей приложения users."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = CustomUserFactory()

    def test_user_creation(self):
        self.assertIsInstance(self.user, CustomUser)
        self.assertTrue(self.user.role == Role.USER)
        self.assertTrue(
            Notification.objects.filter(
                receiver=self.user,
                text=Notifications.WELCOME.value.format(self.user.username),
            ).exists()
        )
