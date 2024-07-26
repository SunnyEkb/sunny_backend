# Generated by Django 5.0.4 on 2024-07-25 10:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ads", "0007_alter_adcategory_parent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="adcategory",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="subcategories",
                to="ads.adcategory",
                verbose_name="Высшая категория",
            ),
        ),
    ]