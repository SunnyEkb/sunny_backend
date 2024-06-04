from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self) -> None:
        """On socket connection. Allowed only for authorized users."""
        await self.accept()
        if self.scope['user'] is None:
            await self.close()
            return
        self.user = self.scope['user']
        await self.channel_layer.group_add(
            self.account_id,
            self.channel_name
        )

    async def disconnect(self, code) -> None:
        """On disconnect socket."""
        await self.channel_layer.group_discard(
            self.account_id,
            self.channel_name
        )
        await self.close(code)
