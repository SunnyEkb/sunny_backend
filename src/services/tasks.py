import os
import shutil

from celery import shared_task
from django.conf import settings


def delete_image_files(path: str):
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, path)):
        os.remove(os.path.join(settings.MEDIA_ROOT, path))


def delete_images_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, path))


@shared_task
def delete_image_files_task(path: str):
    delete_image_files(path)


@shared_task
def delete_images_dir_task(path: str):
    delete_images_dir(path)
