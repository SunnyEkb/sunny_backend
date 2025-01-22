import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

from core.choices import AdvertisementStatus, AdState, CommentStatus
from ads.models import AdImage
from services.models import ServiceImage
from users.models import Favorites
from tests import factories

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
        cls.file_name_1 = "small_1.gif"
        cls.file_name_2 = "small_2.gif"
        cls.uploaded = SimpleUploadedFile(
            name=cls.file_name_1, content=small_gif, content_type="image/gif"
        )
        cls.uploaded_2 = SimpleUploadedFile(
            name=cls.file_name_2, content=small_gif, content_type="image/gif"
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
        cls.user_1 = factories.CustomUserFactory()
        cls.user_2 = factories.CustomUserFactory(password=cls.password)
        cls.user_3 = factories.CustomUserFactory()
        cls.user_4 = factories.CustomUserFactory(password=cls.password)
        cls.unverified_user = factories.CustomUserFactory(
            password=cls.password, is_active=False
        )
        cls.user_for_deletion = factories.CustomUserFactory()

        cls.client_1 = APIClient()
        cls.client_1.force_authenticate(cls.user_1)
        cls.client_2 = APIClient()
        cls.client_2.force_authenticate(cls.user_2)
        cls.client_3 = APIClient()
        cls.client_3.force_authenticate(cls.user_3)
        cls.client_4 = APIClient()
        cls.client_4.force_authenticate(cls.user_4)
        cls.anon_client = APIClient()
        cls.client_for_deletion = APIClient()
        cls.client_for_deletion.force_authenticate(cls.user_for_deletion)


class TestServiceFixtures(TestUserFixtures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.type_1 = factories.TypeFactory()
        cls.type_2 = factories.TypeFactory(parent=cls.type_1)
        cls.service_1 = factories.ServiceFactory(provider=cls.user_1)
        cls.service_1.type.set([cls.type_1])
        cls.service_2 = factories.ServiceFactory(
            provider=cls.user_2,
            status=AdvertisementStatus.PUBLISHED.value,
        )
        cls.service_2_image = ServiceImage.objects.create(
            service=cls.service_2, image=cls.uploaded_2
        )
        cls.service_3 = factories.ServiceFactory(
            provider=cls.user_2,
            status=AdvertisementStatus.HIDDEN.value,
        )
        cls.service_4 = factories.ServiceFactory(provider=cls.user_2)
        cls.service_4.type.set([cls.type_2])
        cls.service_5 = factories.ServiceFactory(provider=cls.user_2)
        cls.service_5.type.set([cls.type_2])
        cls.service_6 = factories.ServiceFactory(
            provider=cls.user_2,
            status=AdvertisementStatus.PUBLISHED.value,
        )
        cls.service_6.type.set([cls.type_2])
        cls.draft_service = factories.ServiceFactory(
            provider=cls.user_3, status=AdvertisementStatus.DRAFT.value
        )
        cls.published_service = factories.ServiceFactory(
            provider=cls.user_3, status=AdvertisementStatus.PUBLISHED.value
        )
        cls.cancelled_service = factories.ServiceFactory(
            provider=cls.user_3, status=AdvertisementStatus.CANCELLED.value
        )
        cls.changed_service = factories.ServiceFactory(
            provider=cls.user_3, status=AdvertisementStatus.CHANGED.value
        )
        cls.moderate_service = factories.ServiceFactory(
            provider=cls.user_3, status=AdvertisementStatus.MODERATION.value
        )
        cls.hidden_service = factories.ServiceFactory(
            provider=cls.user_3, status=AdvertisementStatus.MODERATION.value
        )
        cls.service_del = factories.ServiceFactory(
            provider=cls.user_for_deletion,
            status=AdvertisementStatus.PUBLISHED.value,
        )
        cls.service_del_image = ServiceImage.objects.create(
            service=cls.service_del, image=cls.uploaded_2
        )
        cls.service_del.type.set([cls.type_2])
        cls.service_title = "Super_service"
        cls.new_service_title = "New_super_service"
        cls.service_data = {
            "title": cls.service_title,
            "description": "Some_service",
            "experience": 12,
            "place_of_provision": "Выезд",
            "type_id": cls.type_1.id,
            "salon_name": "Some Name",
            "address": "Some Address",
        }
        cls.comment_1 = factories.CommentFactory(
            subject=cls.published_service,
            author=cls.user_1,
            status=CommentStatus.PUBLISHED.value,
        )
        cls.comment_2 = factories.CommentFactory(
            subject=cls.published_service,
            author=cls.user_2,
            status=CommentStatus.PUBLISHED.value,
        )
        cls.comment_data = {
            "rating": 2,
            "feedback": "Some feadback",
        }
        cls.image_data = {"image": cls.uploaded}
        Favorites.objects.create(
            user=cls.user_2,
            object_id=cls.published_service.id,
            content_type=ContentType.objects.get(
                app_label="services", model="service"
            ),
        )


class TestAdsFixtures(TestUserFixtures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_1 = factories.CategoryFactory()
        cls.category_2 = factories.CategoryFactory(parent=cls.category_1)
        cls.ad_1 = factories.AdFactory(provider=cls.user_1)
        cls.ad_1.category.set([cls.category_1])
        cls.ad_2 = factories.AdFactory(
            provider=cls.user_2,
            status=AdvertisementStatus.PUBLISHED.value,
        )
        cls.ad_2.category.set([cls.category_2])
        cls.ad_2_image = AdImage.objects.create(
            ad=cls.ad_2, image=cls.uploaded
        )
        cls.ad_draft = factories.AdFactory(
            provider=cls.user_2,
        )
        cls.ad_draft.category.set([cls.category_1])
        cls.ad_hidden = factories.AdFactory(
            provider=cls.user_2,
            status=AdvertisementStatus.HIDDEN.value,
        )
        cls.ad_hidden.category.set([cls.category_1])
        cls.ad_title = "Super_ad"
        cls.new_ad_title = "New_Super_ad"
        cls.ad_data = {
            "title": cls.ad_title,
            "description": "Some_ad",
            "price": "100.00",
            "category_id": cls.category_1.id,
            "condition": AdState.USED.value,
        }
        cls.new_ad_data = {
            "title": cls.ad_title,
            "description": "New_description",
            "price": "500.00",
            "category_id": cls.category_1.id,
            "condition": AdState.NEW.value,
        }
        Favorites.objects.create(
            user=cls.user_3,
            object_id=cls.ad_2.id,
            content_type=ContentType.objects.get(app_label="ads", model="ad"),
        )
        cls.ad_to_del = factories.AdFactory(
            provider=cls.user_for_deletion,
            status=AdvertisementStatus.PUBLISHED.value,
        )
        cls.ad_to_del_image = AdImage.objects.create(
            ad=cls.ad_to_del, image=cls.uploaded_2
        )
        cls.ad_to_del.category.set([cls.category_2])
        cls.comment_data = {
            "rating": 2,
            "feedback": "Some feadback",
        }
        cls.comment_1 = factories.CommentFactory(
            subject=cls.ad_2,
            author=cls.user_1,
            status=CommentStatus.PUBLISHED.value,
        )
        cls.comment_2 = factories.CommentFactory(
            subject=cls.ad_1,
            author=cls.user_1,
        )
