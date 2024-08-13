from http import HTTPStatus

from django.urls import reverse

from core.fixtures import TestServiceFixtures
from comments.models import Comment


class TestCommentsView(TestServiceFixtures):
    def test_get_comments_by_authenticated_client(self):
        response = self.client_1.get(
            reverse("comments-list", kwargs={"pk": self.service_1.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response.json()["results"]),
            len(Comment.objects(subject=self.service_1)),
        )
