from channels.testing import WebsocketCommunicator

from core.fixtures import TestUserFixtures
from notifications.consumers import NotificationConsumer


class NotificationConsumerTest(TestUserFixtures):
    async def test_anon_connect(self):
        communicator_anon = WebsocketCommunicator(
            NotificationConsumer.as_asgi(), "/notifications/"
        )
        connected_anon, _ = await communicator_anon.connect()
        self.assertFalse(connected_anon)

    async def test_user_connect(self):
        headers = [
            (b"origin", b"..."),
            (
                b"cookie",
                self.client_1.cookies.output(header="", sep="; ").encode(),
            ),
        ]
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(), "/notifications/", headers
        )
        communicator.scope["user"] = self.user_1
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()
