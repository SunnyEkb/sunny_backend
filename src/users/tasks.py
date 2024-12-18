from celery import shared_task

from core.email_services import send_password_reset_token, send_welcome_email


@shared_task
def send_welcome_email_task(instance, token, email):
    send_welcome_email(instance, token, email)


@shared_task
def send_password_reset_token_task(instance, reset_password_token):
    send_password_reset_token(instance, reset_password_token)
