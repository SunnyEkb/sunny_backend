from celery import shared_task

from core.utils import delete_image_files, delete_images_dir


@shared_task
def delete_image_files_task(path: str):
    delete_image_files(path)


@shared_task
def delete_images_dir_task(path: str):
    delete_images_dir(path)
