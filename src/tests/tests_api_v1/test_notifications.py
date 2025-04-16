from http import HTTPStatus

from django.urls import reverse

from notifications.models import Notification
from tests.fixtures import TestNotificationsFixtures


class TestNotificationView(TestNotificationsFixtures):
    def test_get_notifications(self):
        response = self.client_1.get(reverse("notifications-list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response.json()["results"]),
            len(Notification.objects.filter(receiver=self.user_1)),
        )

    def test_anon_client_can_not_get_notifications(self):
        response = self.anon_client.get(reverse("notifications-list"))
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
