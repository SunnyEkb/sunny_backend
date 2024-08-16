import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

from comments.tests.factories import CommentFactory
from core.choices import AdvertisementStatus
from services.tests.factories import ServiceFactory, TypeFactory
from users.tests.factories import CustomUserFactory

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BaseTestCase(APITestCase):
    """
    Базовый класс для тестирования моделей.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.file_name = "small_1.gif"
        cls.uploaded = SimpleUploadedFile(
            name=cls.file_name, content=small_gif, content_type="image/gif"
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


class TestUserFixtures(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = "some_user"
        cls.new_username = "new_user"
        cls.email_1 = "user@foo.com"
        cls.email_2 = "user_2@foo.com"
        cls.password = "super_password"
        cls.new_password = "new_super_password"
        cls.new_phone = "+79000000000"
        cls.last_name = "last_name"
        cls.first_name = "first_name"
        cls.change_user_data = {
            "username": cls.new_username,
            "last_name": cls.last_name,
            "first_name": cls.first_name,
            "phone": cls.new_phone,
        }
        cls.part_change_user_data = {
            "last_name": cls.last_name,
            "phone": cls.new_phone,
        }
        cls.user_1 = CustomUserFactory()
        cls.user_2 = CustomUserFactory(password=cls.password)
        cls.user_3 = CustomUserFactory()
        cls.user_4 = CustomUserFactory(password=cls.password)

        cls.client_1 = APIClient()
        cls.client_1.force_authenticate(cls.user_1)
        cls.client_2 = APIClient()
        cls.client_2.force_authenticate(cls.user_2)
        cls.client_3 = APIClient()
        cls.client_3.force_authenticate(cls.user_3)
        cls.client_4 = APIClient()
        cls.client_4.force_authenticate(cls.user_4)
        cls.anon_client = APIClient()


class TestServiceFixtures(TestUserFixtures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.type_1 = TypeFactory()
        cls.type_2 = TypeFactory(parent=cls.type_1)
        cls.service_1 = ServiceFactory(provider=cls.user_1)
        cls.service_1.type.set([cls.type_1])
        cls.service_2 = ServiceFactory(
            provider=cls.user_2,
            status=AdvertisementStatus.PUBLISHED.value,
        )
        cls.service_3 = ServiceFactory(
            provider=cls.user_2,
            status=AdvertisementStatus.HIDDEN.value,
        )
        cls.service_4 = ServiceFactory(provider=cls.user_2)
        cls.service_4.type.set([cls.type_2])
        cls.service_5 = ServiceFactory(provider=cls.user_2)
        cls.service_5.type.set([cls.type_2])
        cls.service_6 = ServiceFactory(
            provider=cls.user_2,
            status=AdvertisementStatus.PUBLISHED.value,
        )
        cls.service_6.type.set([cls.type_2])
        cls.draft_service = ServiceFactory(
            provider=cls.user_3, status=AdvertisementStatus.DRAFT.value
        )
        cls.published_service = ServiceFactory(
            provider=cls.user_3, status=AdvertisementStatus.PUBLISHED.value
        )
        cls.cancelled_service = ServiceFactory(
            provider=cls.user_3, status=AdvertisementStatus.CANCELLED.value
        )
        cls.changed_service = ServiceFactory(
            provider=cls.user_3, status=AdvertisementStatus.CHANGED.value
        )
        cls.moderate_service = ServiceFactory(
            provider=cls.user_3, status=AdvertisementStatus.MODERATION.value
        )
        cls.hidden_service = ServiceFactory(
            provider=cls.user_3, status=AdvertisementStatus.MODERATION.value
        )
        cls.service_title = "Super_service"
        cls.new_service_title = "Super_service"
        cls.service_data = {
            "title": cls.service_title,
            "description": "Some_service",
            "experience": 12,
            "place_of_provision": "Выезд",
            "type_id": cls.type_1.id,
            "salon_name": "Some Name",
            "address": "Some Address",
        }
        cls.comment_1 = CommentFactory(
            subject=cls.published_service, author=cls.user_1
        )
        cls.comment_2 = CommentFactory(
            subject=cls.published_service, author=cls.user_2
        )
        cls.comment_data = {
            "content_type": ContentType.objects.get(
                app_label="services", model="service"
            ).id,
            "object_id": cls.published_service.id,
            "rating": 2,
            "feedback": "Some feadback",
        }
        cls.image_data = {"image": cls.uploaded}
