from http import HTTPStatus

from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
from django.urls import reverse

from core.choices import ServicePlace, AdvertisementStatus
from services.models import Service, ServiceImage, Type
from tests.fixtures import TestServiceFixtures
from users.models import Favorites


class TestTypeView(TestServiceFixtures):
    def test_get_types(self):
        response_auth_user = self.client_1.get(reverse("types-list"))
        self.assertEqual(response_auth_user.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response_auth_user.json()),
            len(Type.objects.filter(parent=None)),
        )
        response_anon_user = self.client_1.get(reverse("types-list"))
        self.assertEqual(response_anon_user.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response_anon_user.json()),
            len(Type.objects.filter(parent=None)),
        )

    def test_get_type(self):
        response_auth_user = self.client_1.get(
            reverse("types-detail", kwargs={"pk": self.type_1.id})
        )
        self.assertEqual(response_auth_user.status_code, HTTPStatus.OK)

        response_anon_user = self.client_1.get(
            reverse("types-detail", kwargs={"pk": self.type_1.id})
        )
        self.assertEqual(response_anon_user.status_code, HTTPStatus.OK)

    def test_types_filters(self):
        templates = {
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
            len(response_auth_user.json()["results"]),
            len(
                Service.objects.filter(
                    status=AdvertisementStatus.PUBLISHED.value
                )
            ),
        )

    def test_anon_user_get_services_list(self):
        response_anon_user = self.client_1.get(reverse("services-list"))
        self.assertEqual(response_anon_user.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response_anon_user.json()["results"]),
            len(
                Service.objects.filter(
                    status=AdvertisementStatus.PUBLISHED.value
                )
            ),
        )

    def test_services_filters(self):
        templates = {
            "title": [
                self.service_1.title,
                (
                    Service.objects.filter(
                        status=AdvertisementStatus.PUBLISHED.value
                    ).filter(title__icontains=self.service_1.title)
                ),
            ],
            "description": [
                self.service_1.description,
                (
                    Service.objects.filter(
                        status=AdvertisementStatus.PUBLISHED.value
                    ).filter(description__icontains=self.service_1.description)
                ),
            ],
            "type_id": [
                self.type_1.id,
                (
                    Service.objects.filter(
                        status=AdvertisementStatus.PUBLISHED.value
                    ).filter(type__id=self.type_1.id)
                ),
            ],
            "experience_max": [
                1,
                (
                    Service.objects.filter(
                        status=AdvertisementStatus.PUBLISHED.value
                    ).filter(experience__lte=1)
                ),
            ],
            "experience_min": [
                10,
                (
                    Service.objects.filter(
                        status=AdvertisementStatus.PUBLISHED.value
                    ).filter(experience__gte=10)
                ),
            ],
            "place_of_provision": [
                ServicePlace.OPTIONS.value,
                (
                    Service.objects.filter(
                        status=AdvertisementStatus.PUBLISHED.value
                    ).filter(place_of_provision=ServicePlace.OPTIONS.value)
                ),
            ],
            "my_services": [
                True,
                Service.objects.filter(provider=self.user_1),
            ],
            "address": [
                self.service_1.address,
                (
                    Service.objects.filter(
                        status=AdvertisementStatus.PUBLISHED.value
                    ).filter(address__icontains=self.service_1.address)
                ),
            ],
            "salon_name": [
                self.service_1.salon_name,
                (
                    Service.objects.filter(
                        status=AdvertisementStatus.PUBLISHED.value
                    ).filter(salon_name__icontains=self.service_1.salon_name)
                ),
            ],
            "rating": [
                3,
                (
                    Service.cstm_mng.annotate(rating=Avg("comments__rating"))
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
                    reverse("services-list") + f"?{k}={v[0]}"
                )
                self.assertEqual(len(response.data["results"]), len(v[1]))

    def test_get_services_with_wrong_type_id(self):
        wrong_parametres = [-1, "jsgfkjqegk"]
        for k in wrong_parametres:
            with self.subTest(filter=k):
                response = self.client_1.get(
                    reverse("services-list") + f"?type_id={k}"
                )
                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_service_ordering(self):
        templates = {
            "experience": (
                Service.objects.filter(
                    status=AdvertisementStatus.PUBLISHED.value
                ).order_by("experience")
            ),
            "created_at": (
                Service.objects.filter(
                    status=AdvertisementStatus.PUBLISHED.value
                ).order_by("created_at")
            ),
            "-created_at": (
                Service.objects.filter(
                    status=AdvertisementStatus.PUBLISHED.value
                ).order_by("-created_at")
            ),
        }
        for k, v in templates.items():
            with self.subTest(order=k):
                response = self.client_1.get(
                    reverse("services-list") + f"?ordering={k}"
                )
                # ToDo проверить работу тестов для сортировки
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_services_create(self):
        response = self.client_1.post(
            reverse("services-list"), data=self.service_data
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(
            Service.objects.filter(
                title=self.service_title,
                status=AdvertisementStatus.DRAFT.value,
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

    def test_cant_update_service_under_moderation(self):
        response = self.client_3.put(
            reverse(
                "services-detail", kwargs={"pk": self.moderate_service.pk}
            ),
            data=self.service_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_ACCEPTABLE)

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

    def test_service_status_changed_to_draft_after_updation(self):
        self.client_2.put(
            reverse("services-detail", kwargs={"pk": self.service_2.pk}),
            data=self.service_data,
        )
        self.assertEqual(
            Service.objects.get(pk=self.service_1.pk).status,
            AdvertisementStatus.DRAFT.value,
        )

    def test_service_status_changed_to_draft_after_partial_updation(self):
        new_data = {"title": self.new_service_title}
        self.client_1.patch(
            reverse("services-detail", kwargs={"pk": self.service_1.pk}),
            data=new_data,
        )
        self.assertEqual(
            Service.objects.get(pk=self.service_1.pk).status,
            AdvertisementStatus.DRAFT.value,
        )

    def test_services_methods(self):
        # hide method test
        response_1 = self.client_2.post(
            reverse("services-hide", kwargs={"pk": self.service_6.pk})
        )
        self.assertEqual(response_1.status_code, HTTPStatus.OK)
        self.assertEqual(
            Service.objects.get(pk=self.service_6.pk).status,
            AdvertisementStatus.HIDDEN.value,
        )

        # publish method test
        response_2 = self.client_2.post(
            reverse("services-publish", kwargs={"pk": self.service_3.pk})
        )
        self.assertEqual(response_2.status_code, HTTPStatus.OK)
        self.assertEqual(
            Service.objects.get(pk=self.service_3.pk).status,
            AdvertisementStatus.PUBLISHED.value,
        )

    def test_service_delete(self):
        response = self.client_2.delete(
            reverse("services-detail", kwargs={"pk": self.service_5.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(Service.objects.filter(pk=self.service_5.pk).exists())

    def test_owner_can_get_any_of_his_service(self):
        services = [
            self.draft_service,
            self.moderate_service,
            self.hidden_service,
            self.published_service,
        ]
        for service in services:
            with self.subTest(service=service):
                response = self.client_3.get(
                    reverse("services-detail", kwargs={"pk": service.id})
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_not_owner_cant_get_not_published_service(self):
        services = [
            self.draft_service,
            self.moderate_service,
            self.hidden_service,
        ]
        for service in services:
            with self.subTest(service=service):
                response = self.client_2.get(
                    reverse("services-detail", kwargs={"pk": service.id})
                )
                self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_not_owner_can_get_published_service(self):
        response = self.client_2.get(
            reverse(
                "services-detail", kwargs={"pk": self.published_service.id}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_service_is_favorited(self):
        response = self.client_2.get(
            reverse(
                "services-detail", kwargs={"pk": self.published_service.id}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json()["is_favorited"])

    def test_add_service_to_favorite(self):
        response = self.client_4.post(
            reverse(
                "services-add_to_favorites",
                kwargs={"pk": self.published_service.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_anon_user_cant_add_service_to_favorite(self):
        response = self.anon_client.post(
            reverse(
                "services-add_to_favorites",
                kwargs={"pk": self.published_service.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_cant_add_service_to_favorite_twice(self):
        response = self.client_2.post(
            reverse(
                "services-add_to_favorites",
                kwargs={"pk": self.published_service.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_ACCEPTABLE)

    def test_provider_cant_add_service_to_favorite(self):
        response = self.client_3.post(
            reverse(
                "services-add_to_favorites",
                kwargs={"pk": self.published_service.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_ACCEPTABLE)

    def test_delete_service_from_favorite(self):
        response = self.client_2.delete(
            reverse(
                "services-delete_from_favorites",
                kwargs={"pk": self.published_service.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_anon_client_cant_delete_service_from_favorite(self):
        response = self.anon_client.delete(
            reverse(
                "services-delete_from_favorites",
                kwargs={"pk": self.published_service.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_cant_delete_not_favorite_service_from_favorite(self):
        response = self.client_1.delete(
            reverse(
                "services-delete_from_favorites",
                kwargs={"pk": self.published_service.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_ACCEPTABLE)

    def test_add_serviceimage(self):
        data = {"image": self.base64_image}
        response = self.client_1.post(
            reverse("services-add_photo", kwargs={"pk": self.service_1.id}),
            data=data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_service_status_set_to_draft_after_add_image(self):
        data = {"image": self.base64_image}
        self.client_2.post(
            reverse("services-add_photo", kwargs={"pk": self.service_2.id}),
            data=data,
        )
        self.assertEqual(
            Service.objects.get(id=self.service_2.id).status,
            AdvertisementStatus.DRAFT.value,
        )

    def test_cant_add_photo_to_service_under_moderation(self):
        data = {"image": self.base64_image}
        response = self.client_3.post(
            reverse(
                "services-add_photo", kwargs={"pk": self.moderate_service.id}
            ),
            data=data,
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_ACCEPTABLE)

    def test_add_serviceimage_file(self):
        data = {"image": self.uploaded_2}
        response = self.client_1.post(
            reverse("services-add_photo", kwargs={"pk": self.service_1.id}),
            data=data,
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_add_serviceimage_wrong_value(self):
        data = {"image": "some_string"}
        response = self.client_1.post(
            reverse("services-add_photo", kwargs={"pk": self.service_1.id}),
            data=data,
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_add_serviceimage_wrong_extention(self):
        data = {"image": self.wrong_base64_image}
        response = self.client_1.post(
            reverse("services-add_photo", kwargs={"pk": self.service_1.id}),
            data=data,
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_get_service_image(self):
        response = self.client_3.get(
            reverse(
                "serviceimage-detail", kwargs={"pk": self.service_2_image.id}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_delete_ad_image(self):
        response = self.client_2.delete(
            reverse(
                "serviceimage-detail", kwargs={"pk": self.service_2_image.id}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(
            ServiceImage.objects.filter(id=self.service_2_image.id).exists()
        )

    def test_service_deletion_when_provider_is_deleted(self):
        self.assertTrue(
            Service.objects.filter(id=self.service_del.id).exists()
        )
        self.assertTrue(
            ServiceImage.objects.filter(id=self.service_del_image.id).exists()
        )
        response = self.client_for_deletion.delete(
            reverse("users-detail", kwargs={"pk": self.user_for_deletion.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(
            Service.objects.filter(id=self.service_del.id).exists()
        )
        self.assertFalse(
            ServiceImage.objects.filter(id=self.service_del_image.id).exists()
        )

    def test_service_deletes_from_favorites_when_is_getting_hidden(self):
        self.client_3.post(
            reverse("services-hide", kwargs={"pk": self.published_service.id})
        )
        self.assertFalse(
            Favorites.objects.filter(
                object_id=self.published_service.id,
                content_type=ContentType.objects.get(
                    app_label="services", model="service"
                ),
            ).exists()
        )

    def test_service_deletes_from_favorites_when_is_getting_draft(self):
        self.client_3.put(
            reverse(
                "services-detail", kwargs={"pk": self.published_service.pk}
            ),
            data=self.service_data,
        )
        self.assertFalse(
            Favorites.objects.filter(
                object_id=self.published_service.id,
                content_type=ContentType.objects.get(
                    app_label="services", model="service"
                ),
            ).exists()
        )


class TestServivecesModerationView(TestServiceFixtures):
    def test_get_list_of_services_for_moderation(self):
        response = self.client_moderator.get(
            reverse("moderation_services-list")
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response.json()["results"]),
            len(
                Service.objects.filter(
                    status=AdvertisementStatus.MODERATION.value
                )
            ),
        )

    def test_only_moderator_can_get_list_of_services_for_moderation(self):
        response = self.client_1.get(reverse("moderation_services-list"))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_anon_can_not_get_list_of_services_for_moderation(self):
        response = self.anon_client.get(reverse("moderation_services-list"))
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_approve_service(self):
        response = self.client_moderator.post(
            reverse(
                "moderation_services-approve",
                kwargs={"pk": self.moderate_service.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anon_can_not_approve_service(self):
        response = self.anon_client.post(
            reverse(
                "moderation_services-approve",
                kwargs={"pk": self.moderate_service.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_only_moderator_can_approve_service(self):
        response = self.client_1.post(
            reverse(
                "moderation_services-approve",
                kwargs={"pk": self.moderate_service.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_reject_service(self):
        response = self.client_moderator.post(
            reverse(
                "moderation_services-reject",
                kwargs={"pk": self.moderate_service.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anon_can_not_reject_service(self):
        response = self.anon_client.post(
            reverse(
                "moderation_services-reject",
                kwargs={"pk": self.moderate_service.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_only_moderator_can_reject_service(self):
        response = self.client_1.post(
            reverse(
                "moderation_services-reject",
                kwargs={"pk": self.moderate_service.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
