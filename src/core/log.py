import asyncio
import logging

from core.utils import send_error_message, send_error_message_async


class TelegramHandler(logging.Handler):
    """
    Отправка сообщения об ошибке в чат телеграмм.
    """

    def __init__(self, level: int | str = 0) -> None:
        super().__init__(level)

    def emit(self, record):
        try:
            message = self.format(record)
            send_error_message(message)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


class TelegramAsyncHandler(logging.Handler):
    """
    Отправка сообщения об ошибке в чат телеграмм асинхронно.
    """

    def __init__(self, level: int | str = 0) -> None:
        super().__init__(level)

    def emit(self, record):
        try:
            message = self.format(record)
            loop = asyncio.get_event_loop()
            loop.create_task(self._async_emit(message))

        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    async def _async_emit(self, message):
        await send_error_message_async(message)
