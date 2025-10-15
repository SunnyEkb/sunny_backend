from celery import shared_task

from core.email_services import (
    send_password_changed_email,
    send_password_reset_token,
    send_welcome_email,
)
from users.utils import (
    del_exprd_rfrsh_tokens_from_blck_lst,
    delete_expired_tokens,
    delete_files_after_expiration_date,
    save_file_with_user_data,
)


@shared_task
def send_welcome_email_task(username, token, email):
    send_welcome_email(username, token, email)


@shared_task
def send_password_reset_token_task(domain, username, mail_to, key):
    send_password_reset_token(domain, username, mail_to, key)


@shared_task
def send_password_changed_email_task(username: str, mail_to: str):
    send_password_changed_email(username=username, email=mail_to)


@shared_task
def delete_expired_tokens_task():
    delete_expired_tokens()


@shared_task
def del_exprd_rfrsh_tokens_from_blck_lst_task():
    del_exprd_rfrsh_tokens_from_blck_lst()


@shared_task
def delete_files_after_expiration_date_task():
    delete_files_after_expiration_date()


@shared_task
def save_file_with_user_data_task(email, data):
    save_file_with_user_data(email, data)
