# Generated by Django 5.0.4 on 2024-07-25 11:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ads", "0009_alter_adcategory_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="adcategory",
            options={
                "ordering": ["parent_id", "id"],
                "verbose_name": "Категория объявления",
                "verbose_name_plural": "Категории объявлений",
            },
        ),
    ]
