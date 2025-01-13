from django.contrib.auth import get_user_model
from rest_framework.serializers import ValidationError

from core.choices import APIResponses
from core.enums import Limits


User = get_user_model()


def validate_file_size(temp_file):
    """Валидация размера загружаемого файла."""

    if temp_file.size > Limits.MAX_FILE_SIZE.value:
        raise ValidationError(APIResponses.MAX_FILE_SIZE_EXEED.value)


def validate_username(value):
    """Валидация имени пользователя."""

    if (
        len(value) < Limits.USERNAME_MIN_LENGTH.value
        or len(value) > Limits.USERNAME_MAX_LENGTH.value
        or " " in value
    ):
        raise ValidationError(APIResponses.WRONG_USERNAME.value)
    if User.objects.filter(username=value).exists():
        raise ValidationError(APIResponses.USERNAME_EXISTS.value)


def validate_email(value: str):
    """Валидация email."""

    if User.objects.filter(email=value.lower()).exists():
        raise ValidationError(APIResponses.EMAIL_EXISTS.value)


def validate_phone(value: str):
    """Валидация номера телефона."""

    if User.objects.filter(phone=value).exists():
        raise ValidationError(APIResponses.PHONE_EXISTS.value)
