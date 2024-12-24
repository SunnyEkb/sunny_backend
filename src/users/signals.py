from uuid import uuid4
import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created

from core.choices import Notifications
from core.email_services import send_password_reset_token, send_welcome_email
from notifications.models import Notification
from users.models import VerificationToken
from users.tasks import send_welcome_email_task, send_password_reset_token_task

User = get_user_model()


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """

    key = reset_password_token.key
    mail_to = reset_password_token.user.email
    username = reset_password_token.user.username
    domain = get_current_site(instance.request).domain

    if "test" not in sys.argv and settings.PROD_DB is True:
        send_password_reset_token_task.delay(domain, username, mail_to, key)
    else:
        send_password_reset_token(domain, username, mail_to, key)


@receiver(post_save, sender=User)
def notification_created(sender, instance, created, **kwargs):
    if created:
        notification = Notification.objects.create(
            text=Notifications.WELCOME.value.format(instance.username),
            receiver=instance,
        )
        notification.save()


@receiver(post_save, sender=User)
def send_welcome_email_signal(sender, instance, created, **kwargs):
    if created:
        ver_token = VerificationToken.objects.create(
            user=instance, token=uuid4()
        )
        ver_token.save()
        #        if "test" not in sys.argv and settings.PROD_DB is True:
        #            send_welcome_email_task.delay(
        #                username=instance.username,
        #                token=ver_token.token,
        #                email=instance.email,
        #            )
        #        else:
        send_welcome_email(
            username=instance.username,
            token=ver_token.token,
            email=instance.email,
        )
