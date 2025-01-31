import re
from http import HTTPStatus
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from core.choices import APIResponses
from tests.fixtures import TestUserFixtures
from users.models import VerificationToken

User = get_user_model()


class TestUser(TestUserFixtures):
    def setUp(self):
        self.real_email_backend = settings.EMAIL_BACKEND
        settings.EMAIL_BACKEND = (
            "django.core.mail.backends.locmem.EmailBackend"
        )

    def tearDown(self):
        settings.EMAIL_BACKEND = self.real_email_backend

    def test_user_registry(self):
        email = self.email_1
        body = {
            "username": self.username,
            "email": email,
            "phone": self.new_phone,
            "password": self.password,
            "confirmation": self.password,
        }
        response = self.anon_client.post(
            reverse("registry"), data=body, format="json"
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(User.objects.filter(email=email).exists())
        self.assertEqual(
            User.objects.filter(email=email).first().is_active, False
        )

    def test_user_verification(self):
        body = {
            "token": self.unverified_user.verification_token.token,
        }
        response = self.anon_client.post(
            reverse("veryfy_registration"), data=body, format="json"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(User.objects.get(id=self.unverified_user.id).is_active)
        self.assertFalse(
            VerificationToken.objects.filter(
                id=self.unverified_user.verification_token.id
            ).exists()
        )

    def test_user_verification_with_wrong_token(self):
        body = {"token": uuid4()}
        response = self.anon_client.post(
            reverse("veryfy_registration"), data=body, format="json"
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.data, APIResponses.VERIFICATION_FAILED)

    def test_user_verification_without_token(self):
        response = self.anon_client.post(reverse("veryfy_registration"))
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_user_registry_password_validation(self):
        body = {
            "username": self.username,
            "email": self.email_2,
            "phone": self.new_phone,
            "password": self.password,
            "confirmation": f"{self.password}wrong",
        }
        response = self.anon_client.post(
            reverse("registry"), data=body, format="json"
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json().get("non_field_errors", None),
            [APIResponses.PASSWORD_DO_NOT_MATCH.value],
        )

    def test_user_registry_username_validation_long_username(self):
        body = {
            "username": 10 * self.username,
            "email": self.email_2,
            "password": self.password,
            "confirmation": f"{self.password}wrong",
        }
        response = self.anon_client.post(
            reverse("registry"), data=body, format="json"
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json().get("username"),
            [APIResponses.WRONG_USERNAME.value],
        )

    def test_user_registry_username_validation_short_username(self):
        body = {
            "username": "q",
            "email": self.email_2,
            "password": self.password,
            "confirmation": f"{self.password}wrong",
        }
        response = self.anon_client.post(
            reverse("registry"), data=body, format="json"
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json().get("username"),
            [APIResponses.WRONG_USERNAME.value],
        )

    def test_user_registry_username_validation_wrong_symbols(self):
        body = {
            "username": "*&^#(*)",
            "email": self.email_2,
            "password": self.password,
            "confirmation": f"{self.password}wrong",
        }
        response = self.anon_client.post(
            reverse("registry"), data=body, format="json"
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json().get("username"),
            [APIResponses.WRONG_USERNAME.value],
        )

    def test_user_registry_with_existing_username(self):
        body = {
            "username": self.user_1.username,
            "email": self.email_2,
            "password": self.password,
            "confirmation": f"{self.password}wrong",
        }
        response = self.anon_client.post(
            reverse("registry"), data=body, format="json"
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json().get("username"),
            [APIResponses.USERNAME_EXISTS.value],
        )

    def test_user_registry_with_existing_phone(self):
        body = {
            "username": self.username,
            "email": self.email_2,
            "phone": str(self.user_1.phone),
            "password": self.password,
            "confirmation": f"{self.password}wrong",
        }
        response = self.anon_client.post(
            reverse("registry"), data=body, format="json"
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json().get("phone"),
            [APIResponses.PHONE_EXISTS.value],
        )

    def test_user_login(self):
        data = {"email": self.user_2.email, "password": self.password}
        response = self.client_1.post(reverse("login"), data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.data, {"Success": APIResponses.SUCCESS_LOGIN.value}
        )

    def test_user_login_wrong_credentials(self):
        data = {"email": self.user_2.username, "password": self.password}
        response = self.client_1.post(reverse("login"), data=data)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_password_reset(self):
        response_1 = self.anon_client.post(
            reverse("password_reset:reset-password-request"),
            data={"email": self.user_3.email},
        )
        self.assertEqual(response_1.status_code, HTTPStatus.OK)

        email_content = mail.outbox[0].body
        token_re = r"token=([A-Za-z0-9:\-]+)"
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

        response_4 = self.client_3.post(
            reverse("login"),
            data={"email": self.user_3.email, "password": self.new_password},
        )
        self.assertEqual(response_4.status_code, HTTPStatus.OK)
        self.assertEqual(
            response_4.data, {"Success": APIResponses.SUCCESS_LOGIN.value}
        )

    def test_user_logout(self):
        response = self.client_1.post(reverse("logout"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_refresh_tokens(self):
        response = self.anon_client.post(reverse("token_refresh"))
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_password_change_by_anon_client(self):
        response = self.anon_client.post(
            reverse("change_password"),
            data={
                "current_password": self.password,
                "new_password": self.new_password,
                "new_password_confirmation": self.new_password,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_password_change_by_the_same_password(self):
        response = self.client_2.post(
            reverse("change_password"),
            data={
                "current_password": self.password,
                "new_password": self.password,
                "confirmation": self.password,
            },
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.data["password"][0], APIResponses.NOT_SAME_PASSWORD.value
        )

    def test_password_change_by_wrong_password(self):
        response = self.client_2.post(
            reverse("change_password"),
            data={
                "current_password": self.new_password,
                "new_password": self.new_password,
                "confirmation": self.new_password,
            },
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.data["password"][0], APIResponses.WRONG_PASSWORD.value
        )

    def test_password_change(self):
        response = self.client_4.post(
            reverse("change_password"),
            data={
                "current_password": self.password,
                "new_password": self.new_password,
                "confirmation": self.new_password,
            },
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.data, {"Success": APIResponses.PASSWORD_CHANGED.value}
        )

    def test_change_user_info(self):
        response = self.client_1.put(
            reverse("users-detail", kwargs={"pk": self.user_1.id}),
            data=self.change_user_data,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        user = User.objects.get(id=self.user_1.id)
        self.assertEqual(user.first_name, self.first_name)
        self.assertEqual(user.last_name, self.last_name)

    def test_change_user_info_unique_fields_validation(self):
        data = {
            "username": self.user_1.username,
            "last_name": "some_new_last_name",
            "first_name": "some_new_first_name",
            "phone": str(self.user_1.phone),
        }
        response = self.client_1.put(
            reverse("users-detail", kwargs={"pk": self.user_1.id}),
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        user = User.objects.get(id=self.user_1.id)
        self.assertEqual(user.first_name, "some_new_first_name")
        self.assertEqual(user.last_name, "some_new_last_name")

    def test_part_change_user_info(self):
        response = self.client_2.patch(
            reverse("users-detail", kwargs={"pk": self.user_2.id}),
            data=self.part_change_user_data,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        user = User.objects.get(id=self.user_2.id)
        self.assertEqual(user.last_name, self.last_name)

    def test_part_change_user_info_unique_fields_validation(self):
        data = {
            "last_name": self.last_name,
            "phone": str(self.user_2.phone),
            "username": self.user_2.username,
        }
        response = self.client_2.patch(
            reverse("users-detail", kwargs={"pk": self.user_2.id}),
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        user = User.objects.get(id=self.user_2.id)
        self.assertEqual(user.last_name, self.last_name)

    def test_change_user_info_existing_phone(self):
        data = {
            "last_name": self.last_name,
            "phone": str(self.user_1.phone),
            "username": self.user_2.username,
        }
        response = self.client_2.patch(
            reverse("users-detail", kwargs={"pk": self.user_2.id}),
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_anon_client_can_not_change_user_info(self):
        response_1 = self.anon_client.patch(
            reverse("users-detail", kwargs={"pk": self.user_2.id}),
            data=self.part_change_user_data,
            format="json",
        )
        self.assertEqual(response_1.status_code, HTTPStatus.UNAUTHORIZED)

        response_2 = self.anon_client.put(
            reverse("users-detail", kwargs={"pk": self.user_2.id}),
            data=self.change_user_data,
            format="json",
        )
        self.assertEqual(response_2.status_code, HTTPStatus.UNAUTHORIZED)

    def test_get_me(self):
        response = self.client_1.get(reverse("users-me"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["id"], self.user_1.id)

    def test_add_avatar(self):
        data = {"avatar": self.uploaded}
        response = self.client_1.patch(
            reverse("avatar", kwargs={"pk": self.user_1.id}), data=data
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_delete(self):
        response = self.client_for_deletion.delete(
            reverse("users-detail", kwargs={"pk": self.user_for_deletion.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(
            User.objects.filter(id=self.user_for_deletion.id).exists()
        )
