import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402
from django.core.asgi import get_asgi_application  # noqa: E402

from chat.routing import chat_urlpatterns  # noqa: E402
from core.middleware import CookieAuthMiddleware  # noqa: E402
from notifications.routing import websocket_urlpatterns  # noqa: E402

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            CookieAuthMiddleware(URLRouter(websocket_urlpatterns + chat_urlpatterns))
        ),
    }
)
