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
):
    """
    Отправка e-mail.
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


def send_password_reset_token(domain, username, mail_to, key):
    """
    Отправка токена для смены пароля от ЛК на email.
    """

    context = {
        "username": username,
        "reset_password_url": f"https://{domain}/password-forget?token={key}",
    }
    html_template = "email/reset_password.html"
    text_template = "email/reset_password.txt"
    subject = EmailSubjects.PASSWORD_CHANGE.value

    send_email(html_template, text_template, mail_to, context, subject)


def send_welcome_email(username, token, email):
    """
    Отправка приветственного сообщения на email.
    """

    domain = settings.DOMAIN
    verification_url = f"https://{domain}/registry-activate?token={token}"
    context = {
        "username": username,
        "verification_url": verification_url,
    }
    html_template = "email/welcome.html"
    text_template = "email/welcome.txt"
    subject = EmailSubjects.WELCOME.value
    mail_to = email

    send_email(html_template, text_template, mail_to, context, subject)
