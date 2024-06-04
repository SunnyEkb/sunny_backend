from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        await self.accept()
        if self.scope["user"] is None:
            await self.close()
            return
        self.user = self.scope["user"]
        await self.channel_layer.group_add(self.user.id, self.channel_name)

    async def disconnect(self, code) -> None:
        await self.channel_layer.group_discard(self.user.id, self.channel_name)
        await self.close(code)
