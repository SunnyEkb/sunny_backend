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

    def test_send_ad_to_moderation_by_owner(self):
        response = self.client_2.post(
            reverse("ads-moderate", kwargs={"pk": self.ad_draft.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Ad.objects.get(pk=self.ad_draft.pk).status,
            AdvertisementStatus.MODERATION.value,
        )

    def test_not_owner_cant_send_ad_to_moderation(self):
        response = self.client_1.post(
            reverse("ads-moderate", kwargs={"pk": self.ad_draft.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_anon_user_cant_send_ad_to_moderation(self):
        response = self.anon_client.post(
            reverse("ads-moderate", kwargs={"pk": self.ad_draft.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_owner_hides_ad(self):
        response = self.client_2.post(
            reverse("ads-hide", kwargs={"pk": self.ad_2.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Ad.objects.get(pk=self.ad_2.pk).status,
            AdvertisementStatus.HIDDEN.value,
        )

    def test_not_owner_cant_hide_an_ad(self):
        response = self.client_1.post(
            reverse("ads-hide", kwargs={"pk": self.ad_2.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_anon_user_cant_hide_an_ad(self):
        response = self.anon_client.post(
            reverse("ads-hide", kwargs={"pk": self.ad_2.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_owner_cancells_ad(self):
        response = self.client_2.post(
            reverse("ads-cancell", kwargs={"pk": self.ad_2.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Ad.objects.get(pk=self.ad_2.pk).status,
            AdvertisementStatus.CANCELLED.value,
        )

    def test_not_owner_cant_cancell_an_ad(self):
        response = self.client_1.post(
            reverse("ads-cancell", kwargs={"pk": self.ad_2.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_anon_user_cant_cancell_an_ad(self):
        response = self.anon_client.post(
            reverse("ads-cancell", kwargs={"pk": self.ad_2.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
