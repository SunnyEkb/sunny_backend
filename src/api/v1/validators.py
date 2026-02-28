import re

from django.contrib.auth import get_user_model
from rest_framework import exceptions, status
from rest_framework.serializers import ValidationError

from config.settings.base import ALLOWED_IMAGE_FILE_EXTENTIONS
from core.choices import APIResponses
from core.enums import Limits

User = get_user_model()


def validate_file_size(temp_file):
    """Валидация размера загружаемого файла."""
    if temp_file.size > Limits.MAX_FILE_SIZE:
        raise ValidationError(APIResponses.MAX_FILE_SIZE_EXEED)


def validate_file_quantity(value):
    """Валидация количества загружаемых файлов."""
    if len(value) > Limits.MAX_FILE_QUANTITY:
        raise ValidationError(APIResponses.MAX_IMAGE_QUANTITY_EXEED)


def validate_username(value):
    """Валидация имени пользователя."""
    if (
        len(value) < Limits.USERNAME_MIN_LENGTH
        or len(value) > Limits.USERNAME_MAX_LENGTH
        or " " in value
        or not re.match(r"^[\w.@+-]+\Z", value)
    ):
        raise ValidationError(APIResponses.WRONG_USERNAME)
    if User.objects.filter(username=value).exists():
        raise ValidationError(APIResponses.USERNAME_EXISTS)


def validate_username_updating(instance, value):
    """Валидация имени пользователя."""
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


def validate_email(value: str):
    """Валидация email."""
    if User.objects.filter(email=value.lower()).exists():
        raise ValidationError(APIResponses.EMAIL_EXISTS)


def validate_email_length(email: str):
    """Валидация длины email."""
    if len(email) < Limits.MIN_LENGTH_EAMIL or len(email) > Limits.MAX_LENGTH_EAMIL:
        raise ValidationError(APIResponses.INVALID_EMAIL_LENGTH)


def validate_phone(value: str):
    """Валидация номера телефона."""
    if User.objects.filter(phone=value).exists():
        raise ValidationError(APIResponses.PHONE_EXISTS)


def validate_phone_updating(instance, value: str):
    """Валидация номера телефона."""
    user = User.objects.filter(phone=value)
    if user.exists() and instance != user.first():
        raise ValidationError(APIResponses.PHONE_EXISTS)


def validate_id(id):
    try:
        id = int(id)
    except ValueError:
        raise exceptions.ValidationError(
            detail=APIResponses.INVALID_PARAMETR,
            code=status.HTTP_400_BAD_REQUEST,
        )
    if id < 0:
        raise exceptions.ValidationError(
            detail=APIResponses.INVALID_PARAMETR,
            code=status.HTTP_400_BAD_REQUEST,
        )


def validate_base64_field(value):
    if not isinstance(value, str) or not re.match(
        r"data:image\/[a-z]{3,4};base64,[a-zA-Z0-9\/=\+]+=",
        str(value),
    ):
        raise exceptions.ValidationError(APIResponses.WRONG_CONTENT)


def validate_extention(value: str):
    if value.lower() not in ALLOWED_IMAGE_FILE_EXTENTIONS:
        raise exceptions.ValidationError(APIResponses.WRONG_EXTENTION.format(value))
