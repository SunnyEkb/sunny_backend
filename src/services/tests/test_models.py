from core.fixtures import BaseTestCase
from services.models import ServiceImage
from services.tests.factories import ServiceFactory, TypeFactory

from core.choices import ServiceStatus


class ServiceModelsTest(BaseTestCase):
    """Класс для тестирования моделей приложения services."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service_1 = ServiceFactory()
        cls.service_2 = ServiceFactory()
        cls.type_1 = TypeFactory()
        cls.service_1_image = ServiceImage.objects.create(
            service=cls.service_1, image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_service_image_creation(self):
        self.assertEqual(
            self.service_1_image.image, f"services/{self.file_name}"
        )

    def test_models_have_correct_object_names(self):
        model_str_name = {
            str(self.service_1): self.service_1.title,
            str(self.service_1_image): self.service_1_image.service.title,
            str(self.type_1): self.type_1.title,
        }
        for model, title in model_str_name.items():
            with self.subTest(model=model):
                self.assertEqual(model, title)

    def test_models_default_values(self):
        self.assertEqual(self.service_1.status, ServiceStatus.DRAFT.value)

    def test_models_methods(self):
        pass
