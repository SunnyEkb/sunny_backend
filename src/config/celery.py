import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "delete-expired-tokens": {
        "task": "users.tasks.delete_expired_tokens_task",
        "schedule": crontab(minute="00", hour="23"),
    },
}

app.conf.timezone = "UTC"
