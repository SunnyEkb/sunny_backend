from datetime import datetime, timedelta, timezone
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db import transaction
from core.enums import Limits

from users.models import VerificationToken
from users.exceptions import TokenDoesNotExists

User = get_user_model()


def verify_user(token: UUID):
    ver_token = VerificationToken.cstm_mng.get(token=token)
    if ver_token is not None:
        if ver_token.created_at > datetime.now(timezone.utc) - timedelta(
            hours=Limits.REGISTRY_TOKEN_LIFETIME.value
        ):
            with transaction.atomic():
                user = ver_token.user
                user.is_active = True
                user.save()
                ver_token.delete()
    else:
        raise TokenDoesNotExists()
