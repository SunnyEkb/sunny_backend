import logging

from django.conf import settings

from core.utils import send_telegram_message


class TelegramHandler(logging.Handler):
    """
    Отправка сообщения об ошибке в чат телеграмм.
    """

    def __init__(self, level: int | str = 0) -> None:
        super().__init__(level)
        self.chat_id = settings.TELEGRAM_SUPPORT_CHAT_ID

    def emit(self, record):
        try:
            message = self.format(record)
            send_telegram_message(message, self.chat_id)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)
