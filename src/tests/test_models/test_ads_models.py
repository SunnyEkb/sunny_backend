from tests.fixtures import BaseTestCase
from ads.models import AdImage
from tests.factories import AdFactory, CustomUserFactory

from core.choices import AdvertisementStatus, AdState


class AdModelsTest(BaseTestCase):
    """Класс для тестирования моделей приложения ads."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = CustomUserFactory()
        cls.ad_1 = AdFactory(provider=cls.user)
        cls.ad_2 = AdFactory()
        cls.ad_1_image = AdImage.objects.create(
            ad=cls.ad_1, image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_ad_image_creation(self):
        self.assertEqual(
            self.ad_1_image.image,
            f"users/{self.user.id}/ads/{self.ad_1.id}/{self.file_name_1}",
        )

    def test_models_have_correct_object_names(self):
        model_str_name = {
            str(self.ad_1): self.ad_1.title,
            str(self.ad_1_image): self.ad_1_image.ad.title,
        }
        for model, title in model_str_name.items():
            with self.subTest(model=model):
                self.assertEqual(model, title)

    def test_models_default_values(self):
        field_default_value = {
            self.ad_1.status: AdvertisementStatus.DRAFT.value,
            self.ad_1.condition: AdState.USED.value,
        }
        for field, value in field_default_value.items():
            with self.subTest(field=field):
                self.assertEqual(field, value)
