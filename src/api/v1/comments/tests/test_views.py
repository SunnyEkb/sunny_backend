from http import HTTPStatus

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from core.fixtures import TestServiceFixtures
from comments.models import Comment


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
        response = self.client_2.post(
            reverse(
                "comments-list",
                kwargs={
                    "type": "service",
                    "obj_id": self.published_service.id,
                },
            ),
            data=self.comment_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
