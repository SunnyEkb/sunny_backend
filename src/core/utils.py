import logging
from asgiref.sync import async_to_sync

import telegram
from django.conf import settings

logger = logging.getLogger("django")


@async_to_sync
async def send_telegram_message(
    message: str, chat_id: str = settings.TELEGRAM_SUPPORT_CHAT_ID
) -> None:
    """Отправка сообщения в телеграм чат."""

    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    async with bot:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
        )
