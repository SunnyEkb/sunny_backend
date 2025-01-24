from celery import shared_task

from core.utils import (
    delete_images_dir,
    delete_image_files,
    notify_about_moderation,
)


@shared_task
def delete_image_files_task(path: str):
    delete_image_files(path)


@shared_task
def delete_images_dir_task(path: str):
    delete_images_dir(path)


@shared_task
def notify_about_moderation_task(url: str):
    notify_about_moderation(url)
