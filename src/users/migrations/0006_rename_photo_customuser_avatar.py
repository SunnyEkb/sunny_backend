# Generated by Django 5.0.4 on 2024-09-25 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_customuser_photo"),
    ]

    operations = [
        migrations.RenameField(
            model_name="customuser",
            old_name="photo",
            new_name="avatar",
        ),
    ]
