import os
import shutil

from celery import shared_task
from django.conf import settings


@shared_task
def delete_image_files(path: str):
    if os.path.exists(path):
        os.remove(os.path.join(settings.MEDIA_ROOT, path))


@shared_task
def delete_service_images_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, path))
