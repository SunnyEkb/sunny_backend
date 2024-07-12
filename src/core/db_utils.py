from django.core.exceptions import ValidationError

from core.enums import Limits


def validate_image(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    megabyte_limit = Limits.MAX_FILE_SIZE
    if filesize > megabyte_limit:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


def service_image_path(instance: object, filename: str) -> str:
    """Возвращает путь для сохранения фото к услуге."""

    return "services/{}/{}".format(instance.service.id, filename).replace(
        "\\\\", "/"
    )


def ad_image_path(instance: object, filename: str) -> str:
    """Возвращает путь для сохранения фото к объявлению."""

    return "ads/{}/{}".format(instance.ad.id, filename).replace("\\\\", "/")
