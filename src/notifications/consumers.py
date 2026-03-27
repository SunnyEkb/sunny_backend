import json
from typing import Any

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """Обработчик для подключений к уведомлениям."""

    async def connect(self) -> None:
        """Установить соединение."""
        if self.scope.get("user", None) is None:
            await self.close()
            return
        self.user = self.scope["user"]
        await self.accept()
        self.group_name = f"user_{self.user.id}_notifications"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code: Any) -> None:  # noqa: ANN401
        """Отключить соединение.

        Args:
            close_code (Any): код закрытия

        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.close(close_code)

    async def send_notification(self, event: Any) -> None:  # noqa: ANN401
        """Отправить сообщение.

        Args:
            event (Any): событие

        """
        message = event["message"]
        await self.send(text_data=json.dumps(message))
