# Generated by Django 5.0.4 on 2024-12-18 12:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0010_alter_verificationtoken_token"),
    ]

    operations = [
        migrations.AlterField(
            model_name="verificationtoken",
            name="token",
            field=models.UUIDField(verbose_name="Токен"),
        ),
        migrations.AlterField(
            model_name="verificationtoken",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="verification_token",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
    ]
