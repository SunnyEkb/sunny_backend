from itertools import chain
from http import HTTPStatus

from django.urls import reverse

from ads.models import Ad
from core.choices import AdvertisementStatus
from services.models import Service
from tests.fixtures import TestAdvertisementsFixtures


class TestAdvertisementsView(TestAdvertisementsFixtures):
    def test_auth_user_get_advertisements_list(self):
        response = self.client_1.get(reverse("advertisements"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response.json()["results"]),
            len(
                list(
                    chain(
                        Service.objects.filter(
                            status=AdvertisementStatus.PUBLISHED.value,
                        ),
                        Ad.objects.filter(
                            status=AdvertisementStatus.PUBLISHED.value,
                        ),
                    )
                )
            ),
        )

    def test_auth_user_get_advertisements_list_with_category_id(self):
        response = self.client_1.get(
            reverse("advertisements") + f"?category_id={self.category_1.pk}"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response.json()["results"]),
            len(
                list(
                    chain(
                        Service.objects.filter(
                            status=AdvertisementStatus.PUBLISHED.value,
                            category__id=self.category_1.pk,
                        ),
                        Ad.objects.filter(
                            status=AdvertisementStatus.PUBLISHED.value,
                            category__id=self.category_1.pk,
                        ),
                    )
                )
            ),
        )

    def test_anon_user_get_advertisements_list(self):
        response = self.client_1.get(reverse("advertisements"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response.json()["results"]),
            len(
                list(
                    chain(
                        Service.objects.filter(
                            status=AdvertisementStatus.PUBLISHED.value,
                        ),
                        Ad.objects.filter(
                            status=AdvertisementStatus.PUBLISHED.value,
                        ),
                    )
                )
            ),
        )

    def test_get_advertisements_with_unexisting_category_id_parametr(self):
        response = self.client_1.get(
            reverse("advertisements") + "?category_id=1000000"
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_get_advertisements_with_wrong_category_id_parametr(self):
        response = self.client_1.get(
            reverse("advertisements") + "?category_id=aaaa"
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class TestUserAdvertisementsView(TestAdvertisementsFixtures):
    def test_auth_user_get_own_advertisements(self):
        response = self.client_1.get(reverse("my-advertisements"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response.json()["results"]),
            len(
                list(
                    chain(
                        Service.objects.filter(provider=self.user_1),
                        Ad.objects.filter(provider=self.user_1),
                    )
                )
            ),
        )
