import os
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from core.enums import Limits
from users.exceptions import TokenDoesNotExistsError, TokenExpiredError
from users.models import VerificationToken

User = get_user_model()


def verify_user(token: UUID) -> None:
    """Активация аккаунта пользователя.

    Args:
        token (UUID): токен активации

    """
    ver_token = VerificationToken.cstm_mng.filter(token=token)
    if ver_token.exists() is False:
        raise TokenDoesNotExistsError
    ver_token = ver_token.first()
    if ver_token.created_at > datetime.now(UTC) - timedelta(
        hours=Limits.REGISTRY_TOKEN_LIFETIME.value
    ):
        with transaction.atomic():
            user = ver_token.user
            user.is_active = True
            user.save()
            ver_token.delete()
    else:
        raise TokenExpiredError


def delete_expired_tokens() -> None:
    """Удалить просроченные токены активации пользователя.

    Также удаляются данные неподтвержденных пользователей из БД.
    """
    tokens = VerificationToken.cstm_mng.filter(
        created_at__lt=datetime.now(UTC)
        - timedelta(hours=Limits.REGISTRY_TOKEN_LIFETIME.value)
    )
    for token in tokens:
        with transaction.atomic():
            user = token.user
            user.delete()
            token.delete()


def save_file_with_user_data(email: str, data: Any) -> None:
    """Сохранить сведения о пользователе после удаления его аккаунта.

    Args:
        email (str): email пользователя
        data (str): данные пользователя

    """
    date = (datetime.now(UTC) + settings.DATA_RETENTION_PERIOD).strftime("%Y-%m-%d")
    file_path = os.path.join(
        settings.PATH_TO_SAVE_DELETED_USERS_DATA.location,
        f"{email}_{date}.json",
    ).replace("\\\\", "/")
    with open(file_path, "w") as file:
        file.write(data)


def delete_files_after_expiration_date() -> None:
    """Удалить сведения о бывших пользователях.

    После истечения срока хранения данных.
    """
    files = os.listdir(settings.PATH_TO_SAVE_DELETED_USERS_DATA.location)
    for file in files:
        if datetime.now(UTC).date() > datetime.strptime(
            str(file).split("_")[-1].replace(".json", ""), "%Y-%m-%d"
        ):
            os.remove(file)


def del_exprd_rfrsh_tokens_from_blck_lst() -> None:
    """Удалить просроченные refresh токенов из черного списка."""
    black_listed_tokens = BlacklistedToken.objects.filter(
        token__expires_at__lt=datetime.now(UTC)
    )
    for token in black_listed_tokens:
        token.token.delete()
