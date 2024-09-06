from http import HTTPStatus

from django.urls import reverse

from ads.models import Category
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
