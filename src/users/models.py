from typing import Any

from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from core.choices import Role
from core.db_utils import get_path_to_save_image, validate_image
from core.enums import Limits
from services.tasks import delete_images_dir_task
from users.managers import UserManager, VerificationTokenManager


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

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
        unique=True,
        region="RU",
    )
    role = models.CharField(
        verbose_name="Роль",
        choices=Role.choices,
        default=Role.USER,
        max_length=Limits.MAX_LENGTH_USER_ROLE.value,
    )
    avatar = models.ImageField(
        "Фото",
        upload_to=get_path_to_save_image,
        blank=True,
        null=True,
        validators=[validate_image],
    )
    favorites = GenericRelation("Favorites")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ()

    objects = UserManager()

    class Meta:
        """Настройки модели пользователя."""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        default_related_name = "user"
        ordering = ["email"]

    def __str__(self) -> str:
        """Получить строковое представление пользователя.

        Returns:
            str: email пользователя

        """
        return self.email

    @property
    def is_admin(self) -> bool:
        """Определить является ли пользователь администратором.

        Returns:
            bool: пользователь является администратором

        """
        return self.role == Role.ADMIN

    @property
    def is_moderator(self) -> bool:
        """Определить является ли пользователь модератором.

        Returns:
            bool: пользователь является модератором

        """
        return self.role == Role.MODERATOR

    def get_group_id(self) -> str:
        """Получить идентификатор группы пользователя.

        Returns:
            str: идентификатор группы пользователя

        """
        return f"user_{self.id}_notifications"

    def delete_avatar_image(self) -> None:
        """Удалить файл с аватаром."""
        if self.avatar is not None:
            delete_images_dir_task.delay(f"users/{self.id}")

    def serialize_data(self) -> Any:
        """Сериализовать данные пользователя."""
        return serializers.serialize("json", [self])


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
        """Настройки модели избранного."""

        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = ("user", "content_type", "object_id")
        ordering = ["user", "content_type"]

    def __str__(self) -> str:
        """Получить строковое представление модели избранного.

        Returns:
            str: строковое представление модели избранного

        """
        return f"Избранное {self.user}"

    @staticmethod
    def clear_favorites(instance: models.Model) -> None:
        """Удалить объкт из избранного.

        Args:
            instcnse (Model): экземпляр класса

        """
        Favorites.objects.filter(
            content_type=ContentType.objects.get_for_model(instance).id,
            object_id=instance.id,
        ).delete()


class VerificationToken(models.Model):
    """Токен для подтверждения регистрации."""

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="verification_token",
        verbose_name="Пользователь",
    )
    token = models.UUIDField(verbose_name="Токен")
    created_at = models.DateTimeField(
        "Время создания",
        auto_now_add=True,
        db_index=True,
    )

    objects = models.Manager()
    cstm_mng = VerificationTokenManager()

    class Meta:
        """Настройки модели токена."""

        verbose_name = "Токен для подтверждения регистрации"
        verbose_name_plural = "Токены для подтверждения регистрации"
