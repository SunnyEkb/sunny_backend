from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

from core.choices import EmailSubjects


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

    html_body = render_to_string(html_template, context)
    message_text = render_to_string(text_template, context)
    message = EmailMultiAlternatives(
        subject=subject, to=[mail_to], body=message_text
    )
    message.attach_alternative(html_body, "text/html")
    message.send()


def send_password_reset_token(instance, reset_password_token):
    """
    Отправка токена для смены пароля от ЛК на email.
    """

    context = {
        "username": reset_password_token.user.username,
        "reset_password_url": "{}?token={}".format(
            instance.request.build_absolute_uri(
                reverse("password_reset:reset-password-confirm")
            ),
            reset_password_token.key,
        ),
    }
    html_template = "email/reset_password.html"
    text_template = "email/reset_password.txt"
    subject = EmailSubjects.PASSWORD_CHANGE.value
    mail_to = reset_password_token.user.email

    send_email(html_template, text_template, mail_to, context, subject)


def send_welcome_email(username, email):
    """
    Отправка приветственного сообщения на email.
    """

    context = {"username": username}
    html_template = "email/welcome.html"
    text_template = "email/welcome.txt"
    subject = EmailSubjects.WELCOME.value
    mail_to = email

    send_email(html_template, text_template, mail_to, context, subject)
