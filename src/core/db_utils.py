from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.db.models import Model

from core.enums import Limits


def validate_image(fieldfile_obj: File) -> None:
    """
    Проверяет, размер загружаемого файла.

    :param fieldfile_obj: объект файла
    """

    filesize = fieldfile_obj.file.size
    megabyte_limit = Limits.MAX_FILE_SIZE
    if filesize > megabyte_limit:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


def validate_svg(fieldfile_obj: File) -> None:
    """
    Проверяет, что загружаемый файл в формате SVG.

    :param fieldfile_obj: объект файла
    """

    filename = fieldfile_obj.file.name
    if not filename.endswith(".svg"):
        raise ValidationError("File must be SVG.")


def service_image_path(instance: Model, filename: str) -> str:
    """
    Возвращает путь для сохранения фото к услуге.

    :param instance: экземпляр услуги
    :param filename: имя файла
    :return: путь для сохранения файла
    """

    return "services/{}/{}".format(instance.service.id, filename).replace("\\\\", "/")


def comment_image_path(instance: Model, filename: str) -> str:
    """
    Возвращает путь для сохранения фото к комментарию.

    :param instance: экземпляр комментария
    :param filename: имя файла
    :return: путь для сохранения файла
    """

    return "comments/{}/{}".format(instance.comment.id, filename).replace("\\\\", "/")


def ad_image_path(instance: Model, filename: str) -> str:
    """
    Возвращает путь для сохранения фото к объявлению.

    :param instance: экземпляр объявления
    :param filename: имя файла
    :return: путь для сохранения файла
    """

    return "ads/{}/{}".format(instance.ad.id, filename).replace("\\\\", "/")


def user_photo_path(instance: Model, filename: str) -> str:
    """
    Возвращает путь для сохранения фото пользователя.

    :param instance: экземпляр пользователя
    :param filename: имя файла
    :return: путь для сохранения файла
    """

    return "users/{}/{}".format(instance.id, filename).replace("\\\\", "/")


def get_path_to_save_image(instance: Model, filename: str) -> str:
    """
    Возвращает путь для сохранения фйала с изображением.

    :param instance: экземпляр объекта класса Model
    :param filename: имя файла
    :return: путь для сохранения файла
    """

    model_name = instance.__class__.__name__
    if model_name == "CustomUser":
        base = f"users/{instance.id}/"
        prefix = ""
    elif model_name == "AdImage":
        prefix = f"ads/{instance.ad.id}/"
        base = f"users/{instance.ad.provider.id}/"
    elif model_name == "ServiceImage":
        prefix = f"services/{instance.service.id}/"
        base = f"users/{instance.service.provider.id}/"
    elif model_name == "CommentImage":
        prefix = f"comments/{instance.comment.id}/"
        base = f"users/{instance.comment.author.id}/"

    return base + prefix + filename
