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
    "delete-expired-black-listed-tokens": {
        "task": "users.tasks.del_exprd_rfrsh_tokens_from_blck_lst_task",
        "schedule": crontab(minute="30", hour="23"),
    },
    "delete-expired-files": {
        "task": "users.tasks.delete_files_after_expiration_date",
        "schedule": crontab(day_of_month="15"),
    },
}

app.conf.timezone = "UTC"
