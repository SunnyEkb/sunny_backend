# Generated by Django 5.0.4 on 2024-10-18 16:25

import core.db_utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_rename_photo_customuser_avatar"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="avatar",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=core.db_utils.user_photo_path,
                verbose_name="Фото",
            ),
        ),
    ]