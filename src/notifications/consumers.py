import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        if self.scope.get("user", None) is None:
            await self.close()
            return
        self.user = self.scope["user"]
        await self.accept()
        self.group_name = "user_{0}_notifications".format(self.user.id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, code) -> None:
        await self.channel_layer.group_discard(
            self.group_name, self.channel_name
        )
        await self.close(code)

    async def send_notification(self, event) -> None:
        message = event["message"]
        await self.send(text_data=json.dumps(message))
