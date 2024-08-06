from core.fixtures import BaseTestCase
from comments.models import CommentImage
from comments.tests.factories import CommentFactory
from services.tests.factories import ServiceFactory


class CommentModelsTest(BaseTestCase):
    """Класс для тестирования моделей приложения comments."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service_1 = ServiceFactory()
        cls.comment_1 = CommentFactory(subject=cls.service_1)
        cls.comment_1_image = CommentImage.objects.create(
            comment=cls.comment_1, image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_comment_image_creation(self):
        self.assertEqual(
            self.comment_1_image.image,
            f"comments/{self.service_1.id}/{self.file_name}",
        )

    def test_models_have_correct_object_names(self):
        model_str_name = {
            str(self.comment_1): self.comment_1.feedback[:30],
            str(self.comment_1_image): (
                self.comment_1_image.comment.feedback[:30]
            ),
        }
        for model, title in model_str_name.items():
            with self.subTest(model=model):
                self.assertEqual(model, title)
