from typing import TYPE_CHECKING, Optional, Tuple

from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

if TYPE_CHECKING:
    from django.http import HttpRequest

    from users.models import CustomUser


def enforce_csrf(request: "HttpRequest") -> None:
    """Проверить CSRF.

    Args:
        request (HttpRequest): HTTP запрос

    Raises:
        PermissionDenied: отсутствуют права доступа

    """
    check = authentication.CSRFCheck(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        message = f"CSRF Failed: {reason}"
        raise exceptions.PermissionDenied(message)


class CustomAuthentication(JWTAuthentication):
    """Кастомная аутентификация через Cookie."""

    def authenticate(
        self, request: "HttpRequest"
    ) -> Optional[Tuple["CustomUser", str]]:
        """Аутентифицировать пользователя.

        Args:
            request (HttpRequest): HTTP запрос

        Returns:
           Optional[CustomUser]: Пользователь, если найден

        """
        header = self.get_header(request)

        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"]) or None
        else:
            raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        #        enforce_csrf(request)  !!!!!!!!!!!
        return self.get_user(validated_token), validated_token
