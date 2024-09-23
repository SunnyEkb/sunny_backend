from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from core.choices import Role
from core.db_utils import user_photo_path, validate_image
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
    role = models.CharField(
        verbose_name="Роль",
        choices=Role.choices,
        default=Role.USER,
        max_length=Limits.MAX_LENGTH_USER_ROLE.value,
    )
    photo = models.ImageField(
        "Фото",
        upload_to=user_photo_path,
        blank=True,
        null=True,
        validators=[validate_image],
    )
    favorites = GenericRelation("Favorites")

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


class Favorites(models.Model):
    """Избранное."""

    limit = models.Q(app_label="services", model="service") | models.Q(
        app_label="ads", model="ad"
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favorites",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Что в избранном",
        limit_choices_to=limit,
    )
    object_id = models.PositiveIntegerField("ID объекта")
    subject = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = ("user", "content_type", "object_id")
        ordering = ["user", "content_type"]

    def __str__(self) -> str:
        return f"Избранное {self.user}"
