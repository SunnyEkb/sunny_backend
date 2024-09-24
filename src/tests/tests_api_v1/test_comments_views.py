from http import HTTPStatus

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from comments.models import Comment
from core.choices import CommentStatus
from tests.fixtures import TestServiceFixtures


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
                )
            ),
        )

    def test_comment_create(self):
        response = self.client_4.post(
            reverse("comments_create-list"),
            data=self.comment_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_user_cant_create_two_comments(self):
        response = self.client_1.post(
            reverse("comments_create-list"),
            data=self.comment_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_anon_client_cant_create_comment(self):
        response = self.anon_client.post(
            reverse("comments_create-list"),
            data=self.comment_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_not_author_cant_delete_comment(self):
        response = self.client_1.delete(
            reverse(
                "comments_create-detail", kwargs={"pk": self.comment_2.id}
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_anon_user_cant_delete_comment(self):
        response = self.anon_client.delete(
            reverse(
                "comments_create-detail", kwargs={"pk": self.comment_2.id}
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_comment_delete(self):
        response = self.client_2.delete(
            reverse(
                "comments_create-detail", kwargs={"pk": self.comment_2.id}
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_add_image(self):
        response = self.client_2.post(
            reverse(
                "comments_create-add_photo", kwargs={"pk": self.comment_2.id}
            ),
            data=self.image_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anon_user_cant_add_image(self):
        response = self.anon_client.post(
            reverse(
                "comments_create-add_photo", kwargs={"pk": self.comment_2.id}
            ),
            data=self.image_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_not_author_cant_add_image(self):
        response = self.client_1.post(
            reverse(
                "comments_create-add_photo", kwargs={"pk": self.comment_2.id}
            ),
            data=self.image_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
