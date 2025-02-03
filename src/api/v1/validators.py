import re

from django.contrib.auth import get_user_model
from rest_framework import exceptions, status
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
        or not re.match(r"^[\w.@+-]+\Z", value)
    ):
        raise ValidationError(APIResponses.WRONG_USERNAME.value)
    if User.objects.filter(username=value).exists():
        raise ValidationError(APIResponses.USERNAME_EXISTS.value)


def validate_username_updating(instance, value):
    """Валидация имени пользователя."""

    if (
        len(value) < Limits.USERNAME_MIN_LENGTH.value
        or len(value) > Limits.USERNAME_MAX_LENGTH.value
        or " " in value
        or not re.match(r"^[\w.@+-]+\Z", value)
    ):
        raise ValidationError(APIResponses.WRONG_USERNAME.value)

    user = User.objects.filter(username=value)
    if user.exists() and instance != user.first():
        raise ValidationError(APIResponses.PHONE_EXISTS.value)


def validate_email(value: str):
    """Валидация email."""

    if User.objects.filter(email=value.lower()).exists():
        raise ValidationError(APIResponses.EMAIL_EXISTS.value)


def validate_phone(value: str):
    """Валидация номера телефона."""

    if User.objects.filter(phone=value).exists():
        raise ValidationError(APIResponses.PHONE_EXISTS.value)


def validate_phone_updating(instance, value: str):
    """Валидация номера телефона."""

    user = User.objects.filter(phone=value)
    if user.exists() and instance != user.first():
        raise ValidationError(APIResponses.PHONE_EXISTS.value)


def validate_id(id):
    try:
        id = int(id)
    except ValueError:
        raise exceptions.ValidationError(
            detail=APIResponses.INVALID_PARAMETR.value,
            code=status.HTTP_400_BAD_REQUEST,
        )
    if id < 0:
        raise exceptions.ValidationError(
            detail=APIResponses.INVALID_PARAMETR.value,
            code=status.HTTP_400_BAD_REQUEST,
        )
