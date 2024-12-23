# Generated by Django 5.0.4 on 2024-12-18 06:52

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_alter_customuser_avatar"),
    ]

    operations = [
        migrations.CreateModel(
            name="VerificationToken",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "token",
                    models.UUIDField(
                        default=uuid.UUID(
                            "a768ca71-7e22-4661-b82d-c4801a2239fa"
                        )
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="verification_token",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Токен для подтверждения регистрации",
                "verbose_name_plural": "Токены для подтверждения регистрации",
            },
        ),
    ]