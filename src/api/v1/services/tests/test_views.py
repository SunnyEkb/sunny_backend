from http import HTTPStatus

from django.urls import reverse

from core.choices import ServicePlace, ServiceStatus
from core.fixtures import TestServiceFixtures
from services.models import Service, Type


class TestTypeView(TestServiceFixtures):
    def test_get_types(self):
        response_auth_user = self.client_1.get(reverse("types-list"))
        self.assertEqual(response_auth_user.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response_auth_user.json()), len(Type.objects.all())
        )
        response_anon_user = self.client_1.get(reverse("types-list"))
        self.assertEqual(response_anon_user.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response_anon_user.json()), len(Type.objects.all())
        )

    def test_types_filters(self):
        templates = {
            "category": [
                self.type_1.category,
                Type.objects.filter(category=self.type_1.category),
            ],
            "title": [
                self.type_1.title,
                Type.objects.filter(title__icontains=self.type_1.title),
            ],
        }
        for k, v in templates.items():
            with self.subTest(filter=k):
                response = self.client_1.get(
                    reverse("types-list") + f"?{k}={v[0]}"
                )
                self.assertEqual(len(response.data), len(v[1]))


class TestServivecesView(TestServiceFixtures):
    def test_auth_user_get_services_list(self):
        response_auth_user = self.client_1.get(reverse("services-list"))
        self.assertEqual(response_auth_user.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response_auth_user.json()),
            len(Service.objects.filter(status=ServiceStatus.PUBLISHED.value)),
        )

    def test_anon_user_get_services_list(self):
        response_anon_user = self.client_1.get(reverse("services-list"))
        self.assertEqual(response_anon_user.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response_anon_user.json()),
            len(Service.objects.filter(status=ServiceStatus.PUBLISHED.value)),
        )

    def test_services_filters(self):
        templates = {
            "category": [
                self.type_1.category,
                (
                    Service.objects.filter(
                        status=ServiceStatus.PUBLISHED.value
                    ).filter(type__category=self.type_1.category)
                ),
            ],
            "type": [
                self.type_1.title,
                (
                    Service.objects.filter(
                        status=ServiceStatus.PUBLISHED.value
                    ).filter(type__title__icontains=self.type_1.title)
                ),
            ],
            "title": [
                self.service_1.title,
                (
                    Service.objects.filter(
                        status=ServiceStatus.PUBLISHED.value
                    ).filter(title__icontains=self.service_1.title)
                ),
            ],
            "experience_max": [
                1,
                (
                    Service.objects.filter(
                        status=ServiceStatus.PUBLISHED.value
                    ).filter(experience__lte=1)
                ),
            ],
            "experience_min": [
                10,
                (
                    Service.objects.filter(
                        status=ServiceStatus.PUBLISHED.value
                    ).filter(experience__gte=10)
                ),
            ],
            "place_of_provision": [
                ServicePlace.OPTIONS.value,
                (
                    Service.objects.filter(
                        status=ServiceStatus.PUBLISHED.value
                    ).filter(place_of_provision=ServicePlace.OPTIONS.value)
                ),
            ],
            "my_services": [
                True,
                Service.objects.filter(provider=self.user_1),
            ],
        }
        for k, v in templates.items():
            with self.subTest(filter=k):
                response = self.client_1.get(
                    reverse("services-list") + f"?{k}={v[0]}"
                )
                self.assertEqual(len(response.data), len(v[1]))
