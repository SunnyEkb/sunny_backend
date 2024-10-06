from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from jwt import decode
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

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
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


class CookieAuthMiddleware:
    """Cookie authentication middleware for Django channels."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        token = scope["cookies"].get(settings.SIMPLE_JWT["AUTH_COOKIE"])
        try:
            UntypedToken(token)
        except (InvalidToken, TokenError):
            scope["user"] = None
            return
        else:
            user_data = decode(
                jwt=token,
                key=settings.SIMPLE_JWT["SIGNING_KEY"],
                algorithms=[settings.SIMPLE_JWT["ALGORITHM"]],
            )
            user = await get_user_from_db(user_data["user_id"])
            scope["user"] = user

        return await self.app(scope, receive, send)
