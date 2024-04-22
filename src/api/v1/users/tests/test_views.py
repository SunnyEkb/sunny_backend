import re
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from core.fixtures import TestUserFixtures

User = get_user_model()


class TestUser(TestUserFixtures):
    def setUp(self):
        self.old_email_backend = settings.EMAIL_BACKEND
        settings.EMAIL_BACKEND = (
            "django.core.mail.backends.locmem.EmailBackend"
        )

    def tearDown(self):
        settings.EMAIL_BACKEND = self.old_email_backend

    def test_user_registry(self):
        email = self.email_1
        body = {
            "email": email,
            "password": self.password,
            "confirmation": self.password
        }
        response = self.anon_client.post(
            reverse("registry"), data=body, format="json"
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(
            User.objects.filter(email=email).exists()
        )

    def test_password_reset(self):
        response_1 = self.anon_client.post(
            reverse("password_reset:reset-password-request"),
            data={"email": self.user_3.email},
        )
        self.assertEqual(response_1.status_code, HTTPStatus.OK)

        email_content = mail.outbox[0].body
        token_re = r": ([A-Za-z0-9:\-]+)"
        match = re.search(token_re, email_content)
        token = match.group(1)

        response_2 = self.anon_client.post(
            reverse("password_reset:reset-password-validate"),
            data={"token": token},
        )
        self.assertEqual(response_2.status_code, HTTPStatus.OK)

        response_3 = self.anon_client.post(
            reverse("password_reset:reset-password-confirm"),
            data={"token": token, "password": self.new_password},
        )
        self.assertEqual(response_3.status_code, HTTPStatus.OK)
