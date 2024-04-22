from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


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


def send_password_reset_token(reset_password_token):
    """
    Отправка токена для смены пароля от ЛК на email.
    """

    context = {
        "username": reset_password_token.user.username,
        "token": reset_password_token.key,
    }
    html_template = "email/reset_password.html"
    text_template = "email/reset_password.txt"
    subject = "Сброс пароля на сервисе Солнечный Екатеринбург"
    mail_to = reset_password_token.user.email

    send_email(html_template, text_template, mail_to, context, subject)
