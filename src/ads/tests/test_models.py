from core.fixtures import BaseTestCase
from ads.models import Ad, AdImage
from ads.tests.factories import AdFactory

from core.choices import AdvertisementStatus


class AdModelsTest(BaseTestCase):
    """Класс для тестирования моделей приложения ads."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ad_1 = AdFactory()
        cls.ad_2 = AdFactory()
        cls.ad_2_image = AdImage.objects.create(
            service=cls.ad_1, image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_service_image_creation(self):
        self.assertEqual(self.ad_2_image.image, f"ads/{self.file_name}")

    def test_models_have_correct_object_names(self):
        model_str_name = {
            str(self.ad_1): self.ad_1.title,
            str(self.ad_2_image): self.ad_2_image.service.title,
        }
        for model, title in model_str_name.items():
            with self.subTest(model=model):
                self.assertEqual(model, title)

    def test_models_default_values(self):
        self.assertEqual(self.ad_1.status, AdvertisementStatus.DRAFT.value)

    def test_service_model_methods(self):
        self.ad_2.send_to_moderation()
        service = Ad.objects.get(pk=self.ad_2.id)
        self.assertEqual(service.status, AdvertisementStatus.MODERATION.value)
        service.cancell()
        self.assertEqual(service.status, AdvertisementStatus.CANCELLED.value)
