from core.choices import Notifications, Role
from notifications.models import Notification
from users.models import CustomUser
from tests.factories import CustomUserFactory
from tests.fixtures import BaseTestCase


class UsersModelsTest(BaseTestCase):
    """Класс для тестирования моделей приложения users."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = CustomUserFactory()
        cls.user.avatar = cls.uploaded
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_user_photo_creation(self):
        self.assertEqual(
            self.user.avatar,
            f"users/{self.user.id}/{self.file_name}",
        )

    def test_user_creation(self):
        self.assertIsInstance(self.user, CustomUser)
        self.assertTrue(self.user.role == Role.USER)
        self.assertTrue(
            Notification.objects.filter(
                receiver=self.user,
                text=Notifications.WELCOME.value.format(self.user.username),
            ).exists()
        )
