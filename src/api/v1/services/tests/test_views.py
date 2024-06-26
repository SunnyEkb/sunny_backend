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

    def test_services_create(self):
        response = self.client_1.post(
            reverse("services-list"), data=self.service_data
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(
            Service.objects.filter(
                title=self.service_title,
                status=ServiceStatus.DRAFT.value,
            ).exists()
        )

    def test_anon_client_can_t_create_service(self):
        response = self.anon_client.post(
            reverse("services-list"), data=self.service_data
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_anon_client_can_t_update_service(self):
        response = self.anon_client.put(
            reverse("services-detail", kwargs={"pk": self.service_1.pk}),
            data=self.service_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_only_provider_can_update_service(self):
        response = self.client_2.put(
            reverse("services-detail", kwargs={"pk": self.service_1.pk}),
            data=self.service_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_service_update(self):
        # put method test
        response = self.client_1.put(
            reverse("services-detail", kwargs={"pk": self.service_1.pk}),
            data=self.service_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Service.objects.get(pk=self.service_1.pk).title, self.service_title
        )

        # patch method test
        new_data = {"title": self.new_service_title}
        response = self.client_1.patch(
            reverse("services-detail", kwargs={"pk": self.service_1.pk}),
            data=new_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Service.objects.get(pk=self.service_1.pk).title,
            self.new_service_title,
        )

    def test_services_methods(self):
        # hide method test
        response_1 = self.client_2.post(
            reverse("services-hide", kwargs={"pk": self.service_3.pk})
        )
        self.assertEqual(response_1.status_code, HTTPStatus.OK)
        self.assertEqual(
            Service.objects.get(pk=self.service_3.pk).status,
            ServiceStatus.HIDDEN.value,
        )

        # publish method test
        response_2 = self.client_2.post(
            reverse("services-publish", kwargs={"pk": self.service_3.pk})
        )
        self.assertEqual(response_2.status_code, HTTPStatus.OK)
        self.assertEqual(
            Service.objects.get(pk=self.service_3.pk).status,
            ServiceStatus.PUBLISHED.value,
        )

        # cancell method test
        response_3 = self.client_2.post(
            reverse("services-cancell", kwargs={"pk": self.service_3.pk})
        )
        self.assertEqual(response_3.status_code, HTTPStatus.OK)
        self.assertEqual(
            Service.objects.get(pk=self.service_3.pk).status,
            ServiceStatus.CANCELLED.value,
        )

        # moderate method test
        response_4 = self.client_2.post(
            reverse("services-moderate", kwargs={"pk": self.service_4.pk})
        )
        self.assertEqual(response_4.status_code, HTTPStatus.OK)
        self.assertEqual(
            Service.objects.get(pk=self.service_4.pk).status,
            ServiceStatus.MODERATION.value,
        )
