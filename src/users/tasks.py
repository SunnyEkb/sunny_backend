from typing import Any

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
def send_welcome_email_task(username: str, token: str, email: str) -> None:
    """
    Отложенная задача по отправке приветственного сообщения на email.

    :param username: имя пользователя, которому отправляется письмо
    :param token: токен для подтверждения регистрации
    :param email: адрес отправки письма
    """

    send_welcome_email(username=username, token=token, email=email)


@shared_task
def send_password_reset_token_task(
    domain: str, username: str, mail_to: str, key: str
) -> None:
    """
    Отложенная задача по отправке токена для смены пароля от ЛК на email.

    :param domain: доменное имя сайта
    :param username: имя пользователя, которому отправляется письмо
    :param mail_to: адрес отправки письма
    :param key: токен для смены пароля
    """

    send_password_reset_token(
        domain=domain, username=username, mail_to=mail_to, key=key
    )


@shared_task
def send_password_changed_email_task(username: str, mail_to: str) -> None:
    """
    Отложенная задача по отправке сообщения о смене пароля на email.

    :param username: имя пользователя, которому отправляется письмо
    :param email: адрес отправки письма
    """

    send_password_changed_email(username=username, email=mail_to)


@shared_task
def delete_expired_tokens_task() -> None:
    """
    Периодическая задача по удалению просроченных токенов активации \
        пользователя и данных неподтвержденных пользователей из БД.
    """

    delete_expired_tokens()


@shared_task
def del_exprd_rfrsh_tokens_from_blck_lst_task() -> None:
    """
    Периодическая задача по удалению просроченных refresh \
        токенов из черного списка.
    """

    del_exprd_rfrsh_tokens_from_blck_lst()


@shared_task
def delete_files_after_expiration_date_task():
    """
    Периодическая задача по удалению сведений об удаленных пользователях \
        после истечения срока хранения данных.
    """

    delete_files_after_expiration_date()


@shared_task
def save_file_with_user_data_task(email: str, data: Any) -> None:
    """
    Отложенная задача по сохранению сведений о пользователе \
        после удаления его аккаунта.

    :param email: email пользователя
    :param data: данные пользователя
    """

    save_file_with_user_data(email=email, data=data)
