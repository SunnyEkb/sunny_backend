import logging
import os
import shutil

from asgiref.sync import async_to_sync
from django.conf import settings
import telegram


logger = logging.getLogger("django")


@async_to_sync
async def send_telegram_message(
    message: str, chat_id: str, message_thread_id: str | None
) -> None:
    """Отправка сообщения в телеграм чат."""

    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    async with bot:
        await bot.send_message(
            chat_id=chat_id, text=message, message_thread_id=message_thread_id
        )


def send_error_message(message: str) -> None:
    """Отправка ошибки в телеграм чат."""

    send_telegram_message(
        message=message,
        chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
        message_thread_id=settings.TELEGRAM_SUPPORT_CHAT_TOPIC,
    )


def notify_about_moderation(url: str) -> None:
    """Отправка уведомления о необходимости модерации."""

    send_telegram_message(
        message=f"Необходима модерация. Ссылка: {url}",
        chat_id=settings.TELEGRAM_MODERATORS_CHAT_ID,
        message_thread_id=settings.TELEGRAM_MODERATORS_CHAT_TOPIC,
    )


def delete_image_files(path: str):
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(full_path):
        directory = os.path.dirname(full_path)
        files = os.listdir(directory)
        for file in files:
            full_file_path = os.path.join(directory, file)
            if full_file_path != full_path:
                os.remove(full_file_path)


def delete_images_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, path))
