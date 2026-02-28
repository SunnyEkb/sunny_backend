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

    def test_mark_notification_as_read(self):
        response = self.client_1.post(
            reverse("notifications-mark_as_read", kwargs={"pk": self.notif_1.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Notification.objects.get(id=self.notif_1.id).read)

    def test_anon_client_can_not_mark_notification_as_read(self):
        response = self.anon_client.post(
            reverse("notifications-mark_as_read", kwargs={"pk": self.notif_2.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_not_reciever_can_not_mark_notification_as_read(self):
        response = self.client_2.post(
            reverse("notifications-mark_as_read", kwargs={"pk": self.notif_2.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
