# Generated by Django 5.0.4 on 2024-07-12 07:02

import core.db_utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0008_alter_serviceimage_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="serviceimage",
            name="image",
            field=models.ImageField(
                upload_to=core.db_utils.service_image_path,
                validators=[core.db_utils.validate_image],
                verbose_name="Фото к услуге",
            ),
        ),
    ]
