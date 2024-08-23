# Generated by Django 5.0.4 on 2024-08-16 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0012_service_address_service_salon_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="address",
            field=models.CharField(
                blank=True, max_length=250, null=True, verbose_name="Адрес"
            ),
        ),
        migrations.AlterField(
            model_name="service",
            name="salon_name",
            field=models.CharField(
                blank=True,
                max_length=250,
                null=True,
                verbose_name="Название салона",
            ),
        ),
    ]