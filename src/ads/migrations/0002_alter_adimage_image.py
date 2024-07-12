# Generated by Django 5.0.4 on 2024-07-12 07:02

import core.db_utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ads", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="adimage",
            name="image",
            field=models.ImageField(
                upload_to=core.db_utils.ad_image_path,
                validators=[core.db_utils.validate_image],
                verbose_name="Фото к объявлению",
            ),
        ),
    ]
