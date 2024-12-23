from celery import shared_task

from core.email_services import send_password_reset_token, send_welcome_email
from users.utils import delete_expired_tokens


@shared_task
def send_welcome_email_task(username, token, email):
    send_welcome_email(username, token, email)


@shared_task
def send_password_reset_token_task(domain, username, mail_to, key):
    send_password_reset_token(domain, username, mail_to, key)


@shared_task
def delete_expired_tokens_task():
    delete_expired_tokens()
