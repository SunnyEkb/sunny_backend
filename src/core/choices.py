from django.db import models


class Role(models.IntegerChoices):
    ADMIN = 1
    MODERATOR = 2
    USER = 3


class APIResponses(models.TextChoices):
    PASSWORD_DO_NOT_MATCH = "password and confirmation do not match"
