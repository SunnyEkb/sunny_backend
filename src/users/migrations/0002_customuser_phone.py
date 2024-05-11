# Generated by Django 5.0.4 on 2024-04-26 07:25

import phonenumber_field.modelfields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True,
                max_length=12,
                null=True,
                region=None,
                verbose_name="Номер телефона",
            ),
        ),
    ]