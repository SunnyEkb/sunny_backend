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
    """Создать задачу по отправке приветственного сообщения на email.

    Args:
        username (str): имя пользователя, которому отправляется письмо
        token (str): токен для подтверждения регистрации
        email (str): адрес отправки письма

    """
    send_welcome_email(username=username, token=token, email=email)


@shared_task
def send_password_reset_token_task(
    domain: str, username: str, mail_to: str, key: str
) -> None:
    """Создать задачу по отправке токена для смены пароля от ЛК на email.

    Args:
        domain (str): доменное имя сайта
        username (str): имя пользователя, которому отправляется письмо
        mail_to (str): адрес отправки письма
        key (str): токен для смены пароля

    """
    send_password_reset_token(
        domain=domain, username=username, mail_to=mail_to, key=key
    )


@shared_task
def send_password_changed_email_task(username: str, mail_to: str) -> None:
    """Создать задачу по отправке сообщения о смене пароля на email.

    Args:
        username (str): имя пользователя, которому отправляется письмо
        email (str): адрес отправки письма

    """
    send_password_changed_email(username=username, email=mail_to)


@shared_task
def delete_expired_tokens_task() -> None:
    """Создать задачу по удалению просроченных токенов активации пользователя.

    Также удаляются данные неподтвержденных пользователей из БД.
    """
    delete_expired_tokens()


@shared_task
def del_exprd_rfrsh_tokens_from_blck_lst_task() -> None:
    """Создать задачу по удалению просроченных окенов из черного списка."""
    del_exprd_rfrsh_tokens_from_blck_lst()


@shared_task
def delete_files_after_expiration_date_task() -> None:
    """Создать задачу по удалению сведений о пользователях.

    Сведения удаляются после истечения срока их хранения.
    """
    delete_files_after_expiration_date()


@shared_task
def save_file_with_user_data_task(email: str, data: Any) -> None:
    """Создать задачу по сохранению сведений о пользователе после удаления аккаунта.

    Args:
        email (str): email пользователя
        data (str): данные пользователя

    """
    save_file_with_user_data(email=email, data=data)
