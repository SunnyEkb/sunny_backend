# Generated by Django 5.0.4 on 2024-08-05 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "services",
            "0011_alter_type_options_alter_type_index_together_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="address",
            field=models.CharField(
                max_length=250, null=True, verbose_name="Адрес"
            ),
        ),
        migrations.AddField(
            model_name="service",
            name="salon_name",
            field=models.CharField(
                max_length=250, null=True, verbose_name="Название салона"
            ),
        ),
    ]
