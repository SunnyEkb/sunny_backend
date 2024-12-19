from uuid import UUID

from django.contrib.auth import get_user_model

from users.models import VerificationToken
from users.exceptions import TokenDoesNotExists

User = get_user_model()


def verify_user(token: UUID):
    ver_token = VerificationToken.cstm_mng.get(token=token)
    if ver_token is not None:
        user = ver_token.user
        user.is_active = True
        user.save()
        ver_token.delete()
    else:
        raise TokenDoesNotExists()
