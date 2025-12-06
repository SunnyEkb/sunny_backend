from http import HTTPStatus

from django.urls import reverse

from categories.models import Category
from tests.fixtures import TestAdsFixtures


class TestCategoriesView(TestAdsFixtures):
    def test_get_categories(self):
        response_auth_user = self.client_1.get(
            reverse("common_categories-list")
        )
        self.assertEqual(response_auth_user.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response_auth_user.json()),
            len(Category.objects.filter(parent=None)),
        )

        response_anon_user = self.client_1.get(
            reverse("common_categories-list")
        )
        self.assertEqual(response_anon_user.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response_anon_user.json()),
            len(Category.objects.filter(parent=None)),
        )

    def test_get_category(self):
        response_auth_user = self.client_1.get(
            reverse(
                "common_categories-detail",
                kwargs={"pk": self.category_1.id},
            )
        )
        self.assertEqual(response_auth_user.status_code, HTTPStatus.OK)

        response_anon_user = self.client_1.get(
            reverse(
                "common_categories-detail",
                kwargs={"pk": self.category_1.id},
            )
        )
        self.assertEqual(response_anon_user.status_code, HTTPStatus.OK)

    def test_categories_filters(self):
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
                    reverse("common_categories-list") + f"?{k}={v[0]}"
                )
                self.assertEqual(len(response.data), len(v[1]))
