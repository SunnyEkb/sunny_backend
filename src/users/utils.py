import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import transaction

from core.enums import Limits
from users.models import VerificationToken
from users.exceptions import TokenDoesNotExists, TokenExpired

User = get_user_model()


def verify_user(token: UUID):
    ver_token = VerificationToken.cstm_mng.filter(token=token)
    if ver_token.exists() is False:
        raise TokenDoesNotExists()
    ver_token = ver_token.first()
    if ver_token.created_at > datetime.now(timezone.utc) - timedelta(
        hours=Limits.REGISTRY_TOKEN_LIFETIME.value
    ):
        with transaction.atomic():
            user = ver_token.user
            user.is_active = True
            user.save()
            ver_token.delete()
    else:
        raise TokenExpired()


def delete_expired_tokens():
    tokens = VerificationToken.cstm_mng.filter(
        created_at__lt=datetime.now(timezone.utc)
        - timedelta(hours=Limits.REGISTRY_TOKEN_LIFETIME.value)
    )
    for token in tokens:
        with transaction.atomic():
            user = token.user
            user.delete()
            token.delete()


def save_file_with_user_data(email, data):
    date = (
        datetime.now(timezone.utc) + settings.DATA_RETENTION_PERIOD
    ).strftime("%Y-%m-%d")
    file_path = os.path.join(
        settings.PATH_TO_SAVE_DELETED_USERS_DATA,
        f"{email}_{date}.json",
    )
    with open(file_path) as file:
        file.write(data)


def delete_files_after_expiration_date():
    files = os.listdir(settings.PATH_TO_SAVE_DELETED_USERS_DATA)
    for file in files:
        if datetime.now(timezone.utc).date > datetime.strptime(
            str(file).split("_")[-1].replace(".json", ""), "%Y-%m-%d"
        ):
            os.remove(file)
