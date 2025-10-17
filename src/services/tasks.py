from celery import shared_task

from core.utils import (
    delete_images_dir,
    delete_image_files,
    notify_about_moderation,
)


@shared_task
def delete_image_files_task(path: str) -> None:
    """
    Отложенная задача по удалению файлов из директории.

    :param path: директория для удаления файлов
    """

    delete_image_files(path=path)


@shared_task
def delete_images_dir_task(path: str):
    """
    Отложенная задача по удалению директории.

    :param path: директория для удаления
    """

    delete_images_dir(path=path)


@shared_task
def notify_about_moderation_task(url: str):
    """
    Отложенная задача по отправке уведомления о необходимости модерации.

    :param url: url объекта модерации в админ панели
    """

    notify_about_moderation(url=url)
