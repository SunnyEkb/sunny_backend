from django.urls import re_path

from chat.consumers import ChatConsumer

chat_urlpatterns = [
    re_path(
        r"ws/chat/(?P<id>\d+)/",
        ChatConsumer.as_asgi(),
        name="chat_consumer",
    ),
]
