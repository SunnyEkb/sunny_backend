# Generated by Django 5.0.4 on 2024-08-07 08:21

import django.core.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comments", "0002_comment_created_at_comment_updated_at"),
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="comment",
            options={
                "verbose_name": "Комментарий",
                "verbose_name_plural": "Комментарии",
            },
        ),
        migrations.AlterModelOptions(
            name="commentimage",
            options={
                "verbose_name": "Фото к комментарию",
                "verbose_name_plural": "Фото к комментариям",
            },
        ),
        migrations.AlterField(
            model_name="comment",
            name="rating",
            field=models.PositiveIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(
                        1, "Оценка не может быть меньше 1"
                    ),
                    django.core.validators.MaxValueValidator(
                        5, "Оценка не может быть больше 5"
                    ),
                ],
                verbose_name="Оценка",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="comment",
            unique_together={("author", "content_type", "object_id")},
        ),
    ]