# Generated by Django 5.0.4 on 2024-08-06 08:54

import core.db_utils
import django.core.validators
import django.db.models.deletion
import django.db.models.manager
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Comment",
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
                    "rating",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MaxValueValidator(
                                5, "Оценка не может быть больше 5"
                            )
                        ],
                        verbose_name="Оценка",
                    ),
                ),
                (
                    "feedback",
                    models.CharField(max_length=500, verbose_name="отзыв"),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
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
                        verbose_name="К чему комментарий",
                    ),
                ),
            ],
            managers=[
                ("cstm_mng", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="CommentImage",
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
                    "image",
                    models.ImageField(
                        upload_to=core.db_utils.comment_image_path,
                        validators=[core.db_utils.validate_image],
                        verbose_name="Фото к комментарию",
                    ),
                ),
                (
                    "comment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="comments.comment",
                        verbose_name="Комментарий",
                    ),
                ),
            ],
            options={
                "verbose_name": "Фото к комментарию.",
                "verbose_name_plural": "Фото к комментариям.",
            },
        ),
    ]
