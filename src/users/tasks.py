from celery import shared_task

from core.email_services import send_welcome_email


@shared_task
def send_welcome_email_task(username, email):
    send_welcome_email(username, email)
