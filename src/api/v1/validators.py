import re
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from rest_framework import exceptions, status
from rest_framework.serializers import ValidationError

from config.settings.base import ALLOWED_IMAGE_FILE_EXTENTIONS
from core.choices import APIResponses
from core.enums import Limits

if TYPE_CHECKING:
    from django.core.files import TemporaryUploadedFile

    from users.models import CustomUser

User = get_user_model()


def validate_file_size(temp_file: "TemporaryUploadedFile") -> None:
    """Валидация размера загружаемого файла.

    Args:
        temp_file (TemporaryUploadedFile): файл

    Raises:
        ValidationError: Размер файла превышен

    """
    if temp_file.size > Limits.MAX_FILE_SIZE:
        raise ValidationError(APIResponses.MAX_FILE_SIZE_EXEED)


def validate_file_quantity(value: list) -> None:
    """Валидация количества загружаемых файлов.

    Args:
        value (list): список файлов

    Raises:
        ValidationError: количество загружаемых файлов превышено

    """
    if len(value) > Limits.MAX_FILE_QUANTITY:
        raise ValidationError(APIResponses.MAX_IMAGE_QUANTITY_EXEED)


def validate_username(value: str) -> None:
    """Валидация имени пользователя.

    Args:
        value (str): имя пользователя

    Raises:
        ValidationError: неверное имя пользователя или пользователь \
        с таким именем существует

    """
    if (
        len(value) < Limits.USERNAME_MIN_LENGTH
        or len(value) > Limits.USERNAME_MAX_LENGTH
        or " " in value
        or not re.match(r"^[\w.@+-]+\Z", value)
    ):
        raise ValidationError(APIResponses.WRONG_USERNAME)
    if User.objects.filter(username=value).exists():
        raise ValidationError(APIResponses.USERNAME_EXISTS)


def validate_username_updating(instance: "CustomUser", value: str) -> None:
    """Валидация имени пользователя при изменении его данных.

    Args:
        instance (CustomUser): пользователь
        value (str): ноное значение имени пользователя

    Raises:
        ValidationError: неверное имя пользователя или пользователь \
        с таким именем существует

    """
    if (
        len(value) < Limits.USERNAME_MIN_LENGTH
        or len(value) > Limits.USERNAME_MAX_LENGTH
        or " " in value
        or not re.match(r"^[\w.@+-]+\Z", value)
    ):
        raise ValidationError(APIResponses.WRONG_USERNAME)

    user = User.objects.filter(username=value)
    if user.exists() and instance != user.first():
        raise ValidationError(APIResponses.PHONE_EXISTS)


def validate_email(value: str) -> None:
    """Валидация email на повторение.

    Args:
        value (str): email

    Raises:
        ValidationError: пользователь с таким email существует

    """
    if User.objects.filter(email=value.lower()).exists():
        raise ValidationError(APIResponses.EMAIL_EXISTS)


def validate_email_length(email: str) -> None:
    """Валидация длины email.

    Args:
        email (str): email

    Raises:
        ValidationError: длина email не соовтетсвует требуемой

    """
    if len(email) < Limits.MIN_LENGTH_EAMIL or len(email) > Limits.MAX_LENGTH_EAMIL:
        raise ValidationError(APIResponses.INVALID_EMAIL_LENGTH)


def validate_phone(value: str) -> None:
    """Валидация номера телефона на повторение.

    Args:
        value (str): номер телефона

    Raises:
        ValidationError: пользователь с таким номером телефона существует

    """
    if User.objects.filter(phone=value).exists():
        raise ValidationError(APIResponses.PHONE_EXISTS)


def validate_phone_updating(instance: "CustomUser", value: str) -> None:
    """Валидация номера телефона при обновлении данных пользователя.

    Args:
        value (str): номер телефона
        instance (CustomUser): пользователь

    Raises:
        ValidationError: пользователь с таким номером телефона существует

    """
    user = User.objects.filter(phone=value)
    if user.exists() and instance != user.first():
        raise ValidationError(APIResponses.PHONE_EXISTS)


def validate_id(value: str) -> None:
    """Валидация идентификатора.

    Args:
        value (str): идентификатор

    Raises:
        ValidationError: неверное значение идентификатора

    """
    try:
        value_id = int(value)
    except ValueError as e:
        raise exceptions.ValidationError(
            detail=APIResponses.INVALID_PARAMETR,
            code=status.HTTP_400_BAD_REQUEST,
        ) from e
    if value_id < 0:
        raise exceptions.ValidationError(
            detail=APIResponses.INVALID_PARAMETR,
            code=status.HTTP_400_BAD_REQUEST,
        )


def validate_base64_field(value: str) -> None:
    """Валидировать base64.

    Args:
        value (str): значение

    Raises:
        ValidationError: Значение не валидно

    """
    if not isinstance(value, str) or not re.match(
        r"data:image\/[a-z]{3,4};base64,[a-zA-Z0-9\/=\+]+=",
        str(value),
    ):
        raise exceptions.ValidationError(APIResponses.WRONG_CONTENT)


def validate_extention(value: str) -> None:
    """Валидировать расширение файлов.

    Args:
        value (str): расширение

    Raises:
        ValidationError: расширение не в списке допустимых

    """
    if value.lower() not in ALLOWED_IMAGE_FILE_EXTENTIONS:
        raise exceptions.ValidationError(APIResponses.WRONG_EXTENTION.format(value))
