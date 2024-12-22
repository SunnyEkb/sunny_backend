from rest_framework.serializers import ValidationError

from core.choices import APIResponses
from core.enums import Limits


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
