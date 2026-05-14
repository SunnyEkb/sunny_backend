from typing import TYPE_CHECKING

from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

if TYPE_CHECKING:
    from users.models import CustomUser


def set_refresh_cookie(response: Response, data: dict) -> None:
    """Записать refresh токен в файл куки.

    Args:
        response (Response): Http ответ
        data (dict): данные токена

    """
    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_REFRESH"],
        value=data["refresh"],
        expires=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    )


def set_access_cookie(response: Response, data: dict) -> None:
    """Записать access токен в файл куки.

    Args:
        response (Response): Http ответ
        data (dict): данные токена

    """
    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=data["access"],
        expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    )


def get_tokens_for_user(user: "CustomUser") -> dict:
    """Получить действующий refresh токен пользователя.

    Args:
        user (CustomUser): пользователь

    Returns:
        dict: токены

    """
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
