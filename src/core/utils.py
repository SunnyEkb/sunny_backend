import shutil
from pathlib import Path

import telegram
from asgiref.sync import async_to_sync
from django.conf import settings


@async_to_sync
async def send_telegram_message(
    message: str, chat_id: str, message_thread_id: int | None
) -> None:
    """Отправка сообщения в телеграм чат.

    Args:
        message (str): текст сообщения
        chat_id (str): идентификатор чата
        message_thread_id (int | None): номер подгруппы

    """
    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    async with bot:
        await bot.send_message(
            chat_id=chat_id, text=message, message_thread_id=message_thread_id
        )


async def send_telegram_message_async(
    message: str, chat_id: str, message_thread_id: int | None
) -> None:
    """Отправка сообщения в телеграм чат асинхронно.

    Args:
        message (str): текст сообщения
        chat_id (str): идентификатор чата
        message_thread_id (int | None): номер подгруппы

    """
    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    async with bot:
        await bot.send_message(
            chat_id=chat_id, text=message, message_thread_id=message_thread_id
        )


def send_error_message(message: str) -> None:
    """Отправка ошибки в телеграм чат.

    Args:
        message (str): текст ошибки

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
    """Отправка ошибки в телеграм чат асинхронно.

    Args:
        message (str): текст ошибки

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
    """Отправка уведомления о необходимости модерации.

    Args:
        url (str): url объекта модерации в админ панели

    """
    send_telegram_message(
        message=f"Необходима модерация. Ссылка: {url}",
        chat_id=settings.TELEGRAM_MODERATORS_CHAT_ID,
        message_thread_id=settings.TELEGRAM_MODERATORS_CHAT_TOPIC,
    )


def delete_image_files(path: str) -> None:
    """Удаление файлов из директории.

    Args:
        path (str): директория для удаления файлов

    """
    full_path = Path(settings.MEDIA_ROOT) / path
    if Path(full_path).exists():
        directory = Path.parent(full_path)
        files = Path.iterdir(directory)
        for file in files:
            full_file_path = Path(directory) / file
            if full_file_path != full_path:
                Path.unlink(full_file_path)


def delete_images_dir(path: str) -> None:
    """Удаление директории.

    Args:
        path (str): адрес директории

    """
    if Path(path).exists():
        shutil.rmtree(Path(settings.MEDIA_ROOT) / path)
