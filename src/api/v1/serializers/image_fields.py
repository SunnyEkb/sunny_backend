import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from api.v1.validators import validate_base64_field, validate_extention


class Base64ImageField(serializers.ImageField):
    """Поле для преобразования фото в base64."""

    def to_internal_value(self, data):
        validate_base64_field(data)
        format, imgstr = data.split(";base64,")
        ext = format.split("/")[-1]
        validate_extention(ext)
        data = ContentFile(base64.b64decode(imgstr), name="avatar." + ext)
        return super().to_internal_value(data)
