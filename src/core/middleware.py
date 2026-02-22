from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import parse_cookie
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import UntypedToken

User = get_user_model()


class CsrfHeaderMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if "CSRF_COOKIE" in request.META:
            response["X-CSRFTOKEN"] = request.META["CSRF_COOKIE"]
        return response


@database_sync_to_async
def get_user_from_db(user_id: str):
    """
    Получение пользователя из БД по id.
    """

    try:
        return User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        return None


class CookieAuthMiddleware:
    """Cookie authentication middleware for Django channels."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if "headers" not in scope:
            raise ValueError(
                "CookieMiddleware was passed a scope that did not have a "
                "headers key (make sure it is only passed HTTP or WebSocket "
                "connections)"
            )
        for name, value in scope.get("headers", []):
            if name == b"cookie":
                cookies = parse_cookie(value.decode("latin1"))
                break
        else:
            raise DenyConnection("Empty cookies")

        scope = dict(scope, cookies=cookies)
        token = scope["cookies"].get(settings.SIMPLE_JWT["AUTH_COOKIE"], None)
        try:
            user_id = UntypedToken(token).get("user_id")
        except Exception:
            raise DenyConnection("Invalid token")
        if user_id is None or (user := await get_user_from_db(user_id)) is None:
            raise DenyConnection("User does not exist")
        else:
            scope["user"] = user

        return await self.app(scope, receive, send)
