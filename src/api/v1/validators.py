from rest_framework.serializers import ValidationError

from core.choices import APIResponses
from core.enums import Limits


def validate_file_size(temp_file):
    """Валидация размера загружаемого файла."""

    if temp_file.size > Limits.MAX_FILE_SIZE:
        raise ValidationError(APIResponses.MAX_FILE_SIZE_EXEED.value)
