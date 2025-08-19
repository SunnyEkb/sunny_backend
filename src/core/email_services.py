import logging

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

from core.choices import EmailSubjects

logger = logging.getLogger("django")


def send_email(
    html_template: str,
    text_template: str,
    mail_to: str,
    context: dict,
    subject: str,
) -> None:
    """
    Отправка e-mail.

    :param html_template: шаблон письма в формате html
    :param text_template: шаблон письма в текстовом формате
    :param mail_to: адрес отправки письма
    :param context: словарь с данными для подстановки в шаблон
    :param subject: тема письма
    """

    try:
        html_body = render_to_string(html_template, context)
        message_text = render_to_string(text_template, context)
        message = EmailMultiAlternatives(
            subject=subject, to=[mail_to], body=message_text
        )
        message.attach_alternative(html_body, "text/html")
        message.send()
    except Exception as e:
        logger.exception(e)


def send_password_reset_token(
    domain: str, username: str, mail_to: str, key: str
) -> None:
    """
    Отправка токена для смены пароля от ЛК на email.

    :param domain: доменное имя сайта
    :param username: имя пользователя, которому отправляется письмо
    :param mail_to: адрес отправки письма
    :param key: токен для смены пароля
    """

    context = {
        "username": username,
        "reset_password_url": f"https://{domain}/password-forget?token={key}",
    }

    send_email(
        html_template="email/reset_password.html",
        text_template="email/reset_password.txt",
        mail_to=mail_to,
        context=context,
        subject=EmailSubjects.PASSWORD_CHANGE,
    )


def send_welcome_email(username: str, token: str, email: str) -> None:
    """
    Отправка приветственного сообщения на email.

    :param username: имя пользователя, которому отправляется письмо
    :param token: токен для подтверждения регистрации
    :param email: адрес отправки письма
    """

    context = {
        "username": username,
        "verification_url": (
            f"https://{settings.DOMAIN}/registry-activate?token={token}"
        ),
    }

    send_email(
        html_template="email/welcome.html",
        text_template="email/welcome.txt",
        mail_to=email,
        context=context,
        subject=EmailSubjects.WELCOME,
    )
