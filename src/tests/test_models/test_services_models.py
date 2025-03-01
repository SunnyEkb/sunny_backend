from decimal import Decimal

from django.core.exceptions import FieldDoesNotExist
from django.core.validators import MinValueValidator
from django.db import models
from django.test import TestCase

from core.choices import AdvertisementStatus
from core.constants import LimitsValues
from services.models import Service, ServiceImage, SubService
from tests import factories
from tests.fixtures import BaseTestCase


class ServiceModelsTest(BaseTestCase):
    """Класс для тестирования моделей приложения services."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = factories.CustomUserFactory()
        cls.service_1 = factories.ServiceFactory(provider=cls.user)
        cls.service_2 = factories.ServiceFactory()
        cls.type_1 = factories.TypeFactory()
        cls.service_1_image = ServiceImage.objects.create(
            service=cls.service_1, image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_service_image_creation(self):
        self.assertEqual(
            self.service_1_image.image,
            (
                f"users/{self.user.id}/services/"
                f"{self.service_1.id}/{self.file_name_1}"
            ),
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
        self.assertEqual(
            self.service_1.status, AdvertisementStatus.DRAFT.value
        )


class SubServiceModelTest(TestCase):
    """Класс для тестирования модели SubService."""

    def setUp(self):
        self.user = factories.CustomUserFactory()
        self.service = factories.ServiceFactory(
            provider=self.user,
            title="Основная услуга",
            description="Описание основной услуги",
            experience=5,
            place_of_provision="garage",
        )
        self.correct_title = "Диагностика"
        self.correct_price = Decimal("2000.00")
        self.sub_service = SubService.objects.create(
            title=self.correct_title,
            price=self.correct_price,
            main_service=self.service,
        )

    def test_field_types(self):
        """Тест проверяет типы полей модели."""
        field_types_test_data = [
            {
                "field_name": "title",
                "expected_type": models.CharField,
            },
            {
                "field_name": "price",
                "expected_type": models.DecimalField,
            },
            {
                "field_name": "main_service",
                "expected_type": models.ForeignKey,
            },
            {
                "field_name": "created_at",
                "expected_type": models.DateTimeField,
            },
            {
                "field_name": "updated_at",
                "expected_type": models.DateTimeField,
            },
        ]
        error_message_template = (
            "Тип данных поля {field_name} должен быть {expected_type}."
        )
        for case in field_types_test_data:
            with self.subTest(
                case=case, error_message_template=error_message_template
            ):
                try:
                    field = SubService._meta.get_field(case["field_name"])
                    error_msg = error_message_template.format(
                        field_name=case["field_name"],
                        expected_type=case["expected_type"],
                    )
                    self.assertIsInstance(
                        field,
                        case["expected_type"],
                        error_msg,
                    )
                except FieldDoesNotExist:
                    self.fail(
                        f"Поле {case["field_name"]} должно присутствовать в "
                        f"модели SubService."
                    )

    def test_field_constraints(self):
        """Тест проверяет ограничения полей модели SubService."""
        field_constraints_test_data = [
            {
                "field_name": "title",
                "constraint_name": "max_length",
                "expected_value": LimitsValues.MAX_LENGTH_SUBSERVICE_TITLE,
                "error_message_template": (
                    "Максимальная длина поля {field_name} должна быть "
                    "{expected_value}."
                ),
            },
            {
                "field_name": "price",
                "constraint_name": "max_digits",
                "expected_value": LimitsValues.MAX_DIGITS_PRICE,
                "error_message_template": (
                    "Максимальное количество цифр для поля {field_name} "
                    "должно быть {expected_value}."
                ),
            },
            {
                "field_name": "price",
                "constraint_name": "decimal_places",
                "expected_value": LimitsValues.DECIMAL_PLACES_PRICE,
                "error_message_template": (
                    "Количество знаков после запятой для поля {field_name} "
                    "должно быть {expected_value}."
                ),
            },
        ]

        for case in field_constraints_test_data:
            with self.subTest(case=case):
                try:
                    field = SubService._meta.get_field(case["field_name"])
                    actual_value = getattr(field, case["constraint_name"])
                    error_msg = case["error_message_template"].format(
                        field_name=case["field_name"],
                        expected_value=case["expected_value"],
                    )
                    self.assertEqual(
                        actual_value,
                        case["expected_value"],
                        error_msg,
                    )
                except FieldDoesNotExist:
                    self.fail(
                        f"Поле {case['field_name']} отсутствует в модели "
                        f"SubService."
                    )

    def test_meta_attributes(self):
        """Тест проверяет метаданные модели."""
        meta_attributes_test_data = [
            {
                "attribute": "verbose_name",
                "expected_value": "Услуга прайс-листа",
            },
            {
                "attribute": "verbose_name_plural",
                "expected_value": "Услуги прайс-листа",
            },
        ]
        error_message_template = (
            "Значение атрибута {attribute} должно быть {expected_value}."
        )
        for case in meta_attributes_test_data:
            with self.subTest(
                case=case, error_message_template=error_message_template
            ):
                attribute = getattr(SubService._meta, case["attribute"])
                error_msg = error_message_template.format(
                    attribute=case["attribute"],
                    expected_value=case["expected_value"],
                )
                self.assertEqual(
                    attribute,
                    case["expected_value"],
                    error_msg,
                )

    def test_methods_results(self):
        """Тест проверяет результаты методов модели."""
        methods_test_data = [
            {
                "method": "__str__",
                "real_result": str(self.sub_service),
                "expected_result": self.correct_title,
            },
        ]
        error_message_template = (
            "Результатом метода {method} ожидается {expected_result}, "
            "а фактически {real_result}."
        )
        for case in methods_test_data:
            with self.subTest(
                case=case, error_message_template=error_message_template
            ):
                error_msg = error_message_template.format(
                    method=case["method"],
                    expected_result=case["expected_result"],
                    real_result=case["real_result"],
                )
                self.assertEqual(
                    case["real_result"],
                    case["expected_result"],
                    error_msg,
                )

    def test_fields_related_models(self):
        """Тест проверяет модели на которые ссылаются поля."""
        related_fields_test_data = [
            {
                "field_name": "main_service",
                "expected_related_model": Service,
            },
        ]
        error_message_template = (
            "Ожидается, что поле {field_name} ссылается на модель "
            "{expected_related_model}, а фактически ссылается на "
            "{real_related_model}."
        )
        for case in related_fields_test_data:
            with self.subTest(
                case=case, error_message_template=error_message_template
            ):
                try:
                    real_related_model = SubService._meta.get_field(
                        case["field_name"]
                    ).related_model
                    error_msg = error_message_template.format(
                        field_name=case["field_name"],
                        expected_related_model=case["expected_related_model"],
                        real_related_model=real_related_model,
                    )
                    self.assertEqual(
                        real_related_model,
                        case["expected_related_model"],
                        error_msg,
                    )
                except FieldDoesNotExist:
                    self.fail(
                        f"Поле {case['field_name']} отсутствует в модели "
                        f"SubService."
                    )

    def test_field_validators(self):
        """Тест проверяет наличие валидаторов у полей модели SubService."""
        field_validators_test_data = [
            {
                "field_name": "price",
                "constraint_name": "validators",
                "expected_value": [MinValueValidator],
                "error_message_template": (
                    "Для поля {field_name} должны быть заданы следующие "
                    "валидаторы {expected_value}."
                ),
            },
        ]
        for case in field_validators_test_data:
            with self.subTest(case=case):
                try:
                    real_validators = SubService._meta.get_field(
                        case["field_name"]
                    ).validators
                    with self.subTest(
                        case=case, real_validators=real_validators
                    ):
                        error_msg = case["error_message_template"].format(
                            field_name=case["field_name"],
                            expected_value=case["expected_value"],
                        )
                        for expected_validator in case["expected_value"]:
                            self.assertTrue(
                                any(
                                    isinstance(
                                        real_validator, expected_validator
                                    )
                                    for real_validator in real_validators
                                ),
                                error_msg,
                            )
                except FieldDoesNotExist:
                    self.fail(
                        f"Поле {case['field_name']} отсутствует в модели "
                        f"SubService."
                    )
