from http import HTTPStatus

from django.db.models import Avg
from django.urls import reverse

from ads.models import Ad, AdImage, Category
from core.choices import AdvertisementStatus
from tests.fixtures import TestAdsFixtures


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

    def test_get_type(self):
        response_auth_user = self.client_1.get(
            reverse("categories-detail", kwargs={"pk": self.category_1.id})
        )
        self.assertEqual(response_auth_user.status_code, HTTPStatus.OK)

        response_anon_user = self.client_1.get(
            reverse("categories-detail", kwargs={"pk": self.category_1.id})
        )
        self.assertEqual(response_anon_user.status_code, HTTPStatus.OK)

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

    def test_get_ads_with_wrong_category_id(self):
        wrong_parametres = [-1, "jsgfkjqegk"]
        for k in wrong_parametres:
            with self.subTest(filter=k):
                response = self.client_1.get(
                    reverse("ads-list") + f"?category_id={k}"
                )
                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

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

    def test_owner_publishes_ad(self):
        response = self.client_2.post(
            reverse("ads-publish", kwargs={"pk": self.ad_hidden.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Ad.objects.get(pk=self.ad_2.pk).status,
            AdvertisementStatus.PUBLISHED.value,
        )

    def test_not_owner_cant_publish_an_ad(self):
        response = self.client_1.post(
            reverse("ads-publish", kwargs={"pk": self.ad_hidden.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_anon_user_cant_publish_an_ad(self):
        response = self.anon_client.post(
            reverse("ads-publish", kwargs={"pk": self.ad_hidden.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_ad_create(self):
        response = self.client_1.post(reverse("ads-list"), data=self.ad_data)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(
            Ad.objects.filter(
                title=self.ad_title,
                status=AdvertisementStatus.DRAFT.value,
            ).exists()
        )

    def test_ad_update(self):
        # put method test
        response = self.client_1.put(
            reverse("ads-detail", kwargs={"pk": self.ad_1.pk}),
            data=self.new_ad_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Ad.objects.get(pk=self.ad_1.pk).title, self.new_ad_data["title"]
        )
        self.assertEqual(
            Ad.objects.get(pk=self.ad_1.pk).condition,
            self.new_ad_data["condition"],
        )

        # patch method test
        new_data = {"title": self.new_ad_title}
        response = self.client_1.patch(
            reverse("ads-detail", kwargs={"pk": self.ad_1.pk}),
            data=new_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Ad.objects.get(pk=self.ad_1.pk).title,
            self.new_ad_title,
        )

    def test_add_an_ad_to_favorite(self):
        response = self.client_4.post(
            reverse("ads-add_to_favorites", kwargs={"pk": self.ad_2.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_anon_user_cant_add_an_ad_to_favorite(self):
        response = self.anon_client.post(
            reverse("ads-add_to_favorites", kwargs={"pk": self.ad_1.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_cant_add_an_ad_to_favorite_twice(self):
        response = self.client_3.post(
            reverse("ads-add_to_favorites", kwargs={"pk": self.ad_2.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_ACCEPTABLE)

    def test_provider_cant_add_an_ad_to_favorite(self):
        response = self.client_3.post(
            reverse("ads-add_to_favorites", kwargs={"pk": self.ad_2.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_ACCEPTABLE)

    def test_delete_an_ad_from_favorite(self):
        response = self.client_3.delete(
            reverse("ads-delete_from_favorites", kwargs={"pk": self.ad_2.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_anon_client_cant_delete_an_ad_from_favorite(self):
        response = self.anon_client.delete(
            reverse("ads-delete_from_favorites", kwargs={"pk": self.ad_2.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_cant_delete_not_favorited_ad_from_favorite(self):
        response = self.client_1.delete(
            reverse("ads-delete_from_favorites", kwargs={"pk": self.ad_1.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_ACCEPTABLE)

    def test_an_ad_is_favorited(self):
        response = self.client_3.get(
            reverse("ads-detail", kwargs={"pk": self.ad_2.id})
        )
        self.assertTrue(response.json()["is_favorited"])

    def test_get_ad_image(self):
        response = self.client_3.get(
            reverse("adimage-detail", kwargs={"pk": self.ad_2_image.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_delete_ad_image(self):
        response = self.client_2.delete(
            reverse("adimage-detail", kwargs={"pk": self.ad_2_image.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(
            AdImage.objects.filter(id=self.ad_2_image.id).exists()
        )

    def test_ad_deletion_when_provider_is_deleted(self):
        self.assertTrue(Ad.objects.filter(id=self.ad_to_del.id).exists())
        self.assertTrue(
            AdImage.objects.filter(id=self.ad_to_del_image.id).exists()
        )
        response = self.client_for_deletion.delete(
            reverse("users-detail", kwargs={"pk": self.user_for_deletion.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(Ad.objects.filter(id=self.ad_to_del.id).exists())
        self.assertFalse(
            AdImage.objects.filter(id=self.ad_to_del_image.id).exists()
        )

    def test_ads_filters(self):
        templates = {
            "title": [
                self.ad_1.title,
                (
                    Ad.objects.filter(
                        status=AdvertisementStatus.PUBLISHED.value
                    ).filter(title__icontains=self.ad_1.title)
                ),
            ],
            "description": [
                self.ad_1.description,
                (
                    Ad.objects.filter(
                        status=AdvertisementStatus.PUBLISHED.value
                    ).filter(description__icontains=self.ad_1.description)
                ),
            ],
            "my_ads": [
                True,
                Ad.objects.filter(provider=self.user_1),
            ],
            "rating": [
                3,
                (
                    Ad.cstm_mng.annotate(rating=Avg("comments__rating"))
                    .filter(
                        rating__gte=3,
                        status=AdvertisementStatus.PUBLISHED.value,
                    )
                    .order_by("-created_at")
                ),
            ],
        }
        for k, v in templates.items():
            with self.subTest(filter=k):
                response = self.client_1.get(
                    reverse("ads-list") + f"?{k}={v[0]}"
                )
                self.assertEqual(len(response.data["results"]), len(v[1]))
