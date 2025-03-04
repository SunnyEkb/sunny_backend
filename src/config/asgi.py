import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa
from channels.security.websocket import AllowedHostsOriginValidator  # noqa
from django.core.asgi import get_asgi_application  # noqa

from chat.routing import chat_urlpatterns  # noqa
from core.middleware import CookieAuthMiddleware  # noqa
from notifications.routing import websocket_urlpatterns  # noqa

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            CookieAuthMiddleware(
                URLRouter(websocket_urlpatterns + chat_urlpatterns)
            )
        ),
    }
)
