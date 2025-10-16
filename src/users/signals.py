from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created

from core.choices import Notifications
from notifications.models import Notification
from users.models import VerificationToken
from users.tasks import (
    send_password_changed_email_task,
    send_password_reset_token_task,
    send_welcome_email_task,
)

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
    send_password_reset_token_task.delay(domain, username, mail_to, key)


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
        token = uuid4()
        ver_token = VerificationToken.objects.create(
            user=instance, token=token
        )
        ver_token.save()
        send_welcome_email_task.delay(
            username=instance.username,
            token=token,
            email=instance.email,
        )


@receiver(pre_save, sender=User)
def on_password_change(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        previous_data = User.objects.get(id=instance.id)
        if previous_data.password != instance.password:
            send_password_changed_email_task.delay(
                username=previous_data.username,
                mail_to=previous_data.email,
            )
