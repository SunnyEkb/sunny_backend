# Generated by Django 5.0.4 on 2024-08-23 07:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("users", "0002_alter_customuser_role"),
    ]

    operations = [
        migrations.CreateModel(
            name="Favorites",
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
                    "object_id",
                    models.PositiveIntegerField(verbose_name="ID объекта"),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        limit_choices_to=models.Q(
                            models.Q(
                                ("app_label", "services"), ("model", "service")
                            ),
                            models.Q(("app_label", "ads"), ("model", "ad")),
                            _connector="OR",
                        ),
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                        verbose_name="Что в избранном",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorites",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Избранное",
                "verbose_name_plural": "Избранное",
                "unique_together": {("user", "content_type", "object_id")},
            },
        ),
    ]
