from http import HTTPStatus

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from comments.models import Comment
from core.choices import CommentStatus
from tests.fixtures import TestAdsFixtures, TestServiceFixtures


class TestCommentsView(TestServiceFixtures):
    def test_get_comments_by_authenticated_client(self):
        response = self.client_1.get(
            reverse(
                "comments-list",
                kwargs={
                    "type": "service",
                    "obj_id": self.published_service.id,
                },
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response.json()["results"]),
            len(
                Comment.cstm_mng.filter(
                    content_type=ContentType.objects.get(
                        app_label="services", model="service"
                    ),
                    object_id=self.published_service.id,
                    status=CommentStatus.PUBLISHED.value,
                )
            ),
        )

    def test_get_comments_by_anon_client(self):
        response = self.anon_client.get(
            reverse(
                "comments-list",
                kwargs={
                    "type": "service",
                    "obj_id": self.published_service.id,
                },
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response.json()["results"]),
            len(
                Comment.cstm_mng.filter(
                    content_type=ContentType.objects.get(
                        app_label="services", model="service"
                    ),
                    object_id=self.published_service.id,
                    status=CommentStatus.PUBLISHED.value,
                )
            ),
        )

    def test_get_comments_with_wrong_type(self):
        response = self.anon_client.get(
            reverse(
                "comments-list",
                kwargs={
                    "type": "abc",
                    "obj_id": self.published_service.id,
                },
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_not_author_cant_delete_comment(self):
        response = self.client_1.delete(
            reverse(
                "comments_destroy-detail", kwargs={"pk": self.comment_2.id}
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_anon_user_cant_delete_comment(self):
        response = self.anon_client.delete(
            reverse(
                "comments_destroy-detail", kwargs={"pk": self.comment_2.id}
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_comment_delete(self):
        response = self.client_2.delete(
            reverse(
                "comments_destroy-detail", kwargs={"pk": self.comment_2.id}
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)


class TestCommentsToAdsCreationView(TestAdsFixtures):
    def test_add_comment_to_an_ad(self):
        response = self.client_4.post(
            reverse("ads-add_comment", kwargs={"pk": self.ad_2.id}),
            data=self.comment_data,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_add_comment_without_images_to_an_ad(self):
        response = self.client_3.post(
            reverse("ads-add_comment", kwargs={"pk": self.ad_2.id}),
            data=self.comment_data_without_images,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_user_cant_add_two_comments_to_the_same_ad(self):
        response = self.client_1.post(
            reverse("ads-add_comment", kwargs={"pk": self.ad_2.id}),
            data=self.comment_data,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_ACCEPTABLE)

    def test_anon_client_cant_add_comment_to_an_ad(self):
        response = self.anon_client.post(
            reverse("ads-add_comment", kwargs={"pk": self.ad_2.id}),
            data=self.comment_data,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_cant_add_comment_with_too_much_images(self):
        response = self.client_3.post(
            reverse("ads-add_comment", kwargs={"pk": self.ad_2.id}),
            data=self.comment_data_with_too_much_images,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_cant_add_comment_with_wrong_image_value(self):
        response = self.client_3.post(
            reverse("ads-add_comment", kwargs={"pk": self.ad_2.id}),
            data=self.comment_data_images_wrong_base64,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_cant_add_comment_with_wrong_image_extention(self):
        response = self.client_3.post(
            reverse("ads-add_comment", kwargs={"pk": self.ad_2.id}),
            data=self.comment_data_images_wrong_ext,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class TestCommentsToServicesCreationView(TestServiceFixtures):
    def test_add_comment_without_images_to_service(self):
        response = self.client_4.post(
            reverse(
                "services-add_comment",
                kwargs={"pk": self.published_service.id},
            ),
            data=self.comment_data,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_add_comment_with_images_to_service(self):
        response = self.client_1.post(
            reverse(
                "services-add_comment",
                kwargs={"pk": self.service_2.id},
            ),
            data=self.comment_data_without_images,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_cant_add_comment_with_wrong_image_to_service(self):
        response = self.client_3.post(
            reverse(
                "services-add_comment",
                kwargs={"pk": self.service_2.id},
            ),
            data=self.comment_data_with_wrong_bs64,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_user_cant_add_two_comments_to_the_same_service(self):
        response = self.client_1.post(
            reverse(
                "services-add_comment",
                kwargs={"pk": self.published_service.id},
            ),
            data=self.comment_data,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_ACCEPTABLE)

    def test_anon_client_cant_add_comment_to_service(self):
        response = self.anon_client.post(
            reverse(
                "services-add_comment",
                kwargs={"pk": self.published_service.id},
            ),
            data=self.comment_data,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_comment_data_validation(self):
        test_data = [-1, 0, 30, 1.1, "abc", True]
        for value in test_data:
            data = {"rating": value, "feedback": "feedback"}
            with self.subTest(Wrong_avlue=value):
                response = self.client_1.post(
                    reverse(
                        "services-add_comment",
                        kwargs={"pk": self.published_service.id},
                    ),
                    data=data,
                )
                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class TestCommentsModerationView(TestServiceFixtures):
    def test_get_list_of_comments_for_moderation(self):
        response = self.client_moderator.get(
            reverse("moderation_comments-list")
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response.json()["results"]),
            len(Comment.objects.filter(status=CommentStatus.MODERATION.value)),
        )

    def test_only_moderator_can_get_list_of_comments_for_moderation(self):
        response = self.client_1.get(reverse("moderation_comments-list"))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_anon_can_not_get_list_of_comments_for_moderation(self):
        response = self.anon_client.get(reverse("moderation_comments-list"))
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_approve_comment(self):
        response = self.client_moderator.post(
            reverse(
                "moderation_comments-approve",
                kwargs={"pk": self.cmmnt_for_mdrtn.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anon_can_not_approve_comment(self):
        response = self.anon_client.post(
            reverse(
                "moderation_comments-approve",
                kwargs={"pk": self.cmmnt_for_mdrtn.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_only_moderator_can_approve_comment(self):
        response = self.client_1.post(
            reverse(
                "moderation_comments-approve",
                kwargs={"pk": self.cmmnt_for_mdrtn.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_reject_comment(self):
        response = self.client_moderator.post(
            reverse(
                "moderation_comments-reject",
                kwargs={"pk": self.cmmnt_for_mdrtn.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anon_can_not_reject_comment(self):
        response = self.anon_client.post(
            reverse(
                "moderation_comments-reject",
                kwargs={"pk": self.cmmnt_for_mdrtn.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_only_moderator_can_reject_commente(self):
        response = self.client_1.post(
            reverse(
                "moderation_comments-reject",
                kwargs={"pk": self.cmmnt_for_mdrtn.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
