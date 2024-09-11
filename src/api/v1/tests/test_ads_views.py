from http import HTTPStatus

from django.urls import reverse

from ads.models import Ad, Category
from core.choices import AdvertisementStatus
from core.fixtures import TestAdsFixtures


class TestCategoryView(TestAdsFixtures):
    def test_get_types(self):
        response_auth_user = self.client_1.get(reverse("categories-list"))
        self.assertEqual(response_auth_user.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response_auth_user.json()),
            len(Category.objects.filter(parent=None)),
        )
        response_anon_user = self.client_1.get(reverse("categories-list"))
        self.assertEqual(response_anon_user.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response_anon_user.json()),
            len(Category.objects.filter(parent=None)),
        )

    def test_types_filters(self):
        templates = {
            "title": [
                self.category_1.title,
                Category.objects.filter(
                    title__icontains=self.category_1.title
                ),
            ],
        }
        for k, v in templates.items():
            with self.subTest(filter=k):
                response = self.client_1.get(
                    reverse("categories-list") + f"?{k}={v[0]}"
                )
                self.assertEqual(len(response.data), len(v[1]))


class TestAdView(TestAdsFixtures):
    def test_auth_user_get_ads_list_with_no_category_id(self):
        response_auth_user = self.client_1.get(reverse("ads-list"))
        self.assertEqual(response_auth_user.status_code, HTTPStatus.OK)
        self.assertEqual(len(response_auth_user.json()["results"]), 0)

    def test_anon_user_get_ads_list_with_no_category_id(self):
        response_anon_user = self.client_1.get(reverse("ads-list"))
        self.assertEqual(response_anon_user.status_code, HTTPStatus.OK)
        self.assertEqual(len(response_anon_user.json()["results"]), 0)

    def test_auth_user_get_ads_list_with_category_id(self):
        response_auth_user = self.client_1.get(
            reverse("ads-list") + f"?category_id={self.category_1.id}"
        )
        self.assertEqual(response_auth_user.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response_auth_user.json()["results"]),
            len(
                Ad.objects.filter(
                    status=AdvertisementStatus.PUBLISHED.value,
                    category__id=self.category_1.id,
                )
            ),
        )

    def test_anon_user_get_ads_list_with_category_id(self):
        response_anon_user = self.anon_client.get(
            reverse("ads-list") + f"?category_id={self.category_1.id}"
        )
        self.assertEqual(response_anon_user.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response_anon_user.json()["results"]),
            len(
                Ad.objects.filter(
                    status=AdvertisementStatus.PUBLISHED.value,
                    category__id=self.category_1.id,
                )
            ),
        )
