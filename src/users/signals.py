from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created

from core.choices import Notifications
from core.email_services import send_password_reset_token
from notifications.models import Notification
from users.tasks import send_welcome_email_task

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

    send_password_reset_token(reset_password_token)


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
        send_welcome_email_task.delay(
            username=instance.username,
            email=instance.email,
        )
