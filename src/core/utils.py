import os
import shutil

from asgiref.sync import async_to_sync
from django.conf import settings
import telegram


@async_to_sync
async def send_telegram_message(
    message: str, chat_id: str, message_thread_id: int | None
) -> None:
    """
    Отправка сообщения в телеграм чат.

    :param message: текст сообщения
    :param chat_id: идентификатор чата
    :param message_thread_id: номер подгруппы
    """

    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    async with bot:
        await bot.send_message(
            chat_id=chat_id, text=message, message_thread_id=message_thread_id
        )


async def send_telegram_message_async(
    message: str, chat_id: str, message_thread_id: int | None
) -> None:
    """
    Отправка сообщения в телеграм чат асинхронно.

    :param message: текст сообщения
    :param chat_id: идентификатор чата
    :param message_thread_id: номер подгруппы
    """

    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    async with bot:
        await bot.send_message(
            chat_id=chat_id, text=message, message_thread_id=message_thread_id
        )


def send_error_message(message: str) -> None:
    """
    Отправка ошибки в телеграм чат.

    :param message: текст ошибки
    """

    send_telegram_message(
        message=(
            message
            if len(message) < 4095
            else (message[0:2000] + "\n...\n" + message[-2080:])
        ),
        chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
        message_thread_id=settings.TELEGRAM_SUPPORT_CHAT_TOPIC,
    )


async def send_error_message_async(message: str) -> None:
    """
    Отправка ошибки в телеграм чат асинхронно.

    :param message: текст ошибки
    """

    await send_telegram_message_async(
        message=(
            message
            if len(message) < 4095
            else (message[0:2000] + "\n...\n" + message[-2080:])
        ),
        chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
        message_thread_id=settings.TELEGRAM_SUPPORT_CHAT_TOPIC,
    )


def notify_about_moderation(url: str) -> None:
    """
    Отправка уведомления о необходимости модерации.

    :param url: url объекта модерации в админ панели
    """

    send_telegram_message(
        message=f"Необходима модерация. Ссылка: {url}",
        chat_id=settings.TELEGRAM_MODERATORS_CHAT_ID,
        message_thread_id=settings.TELEGRAM_MODERATORS_CHAT_TOPIC,
    )


def delete_image_files(path: str) -> None:
    """
    Удаление файлов из директории.

    :param path: директория для удаления файлов
    """

    full_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(full_path):
        directory = os.path.dirname(full_path)
        files = os.listdir(directory)
        for file in files:
            full_file_path = os.path.join(directory, file)
            if full_file_path != full_path:
                os.remove(full_file_path)


def delete_images_dir(path: str) -> None:
    """
    Удаление директории.

    :param path: адрес директории
    """

    if os.path.exists(path):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, path))
