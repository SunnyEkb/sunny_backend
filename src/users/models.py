from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from core.choices import Role
from core.enums import Limits
from users.managers import UserManager


class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя.
    """

    first_name = models.CharField(
        verbose_name="Имя",
        max_length=Limits.MAX_LENGTH_FIRST_NAME.value,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=Limits.MAX_LENGTH_LAST_NAME.value,
        blank=True,
        null=True,
    )
    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        unique=True,
        db_index=True,
    )
    phone = PhoneNumberField(
        verbose_name="Номер телефона",
        max_length=Limits.MAX_LENGTH_PHONE_NUMBER.value,
        blank=True,
        null=True,
    )
    role = models.IntegerField(
        verbose_name="Роль",
        choices=Role.choices,
        default=Role.USER,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ()

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        default_related_name = "user"
        ordering = [
            "email",
        ]

    def __str__(self) -> str:
        return self.email

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    @property
    def is_moderator(self):
        return self.role == Role.MODERATOR

    def get_group_id(self):
        return "user_{0}_notifications".format(self.id)
