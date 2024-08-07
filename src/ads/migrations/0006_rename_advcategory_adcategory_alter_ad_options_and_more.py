# Generated by Django 5.0.4 on 2024-07-25 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ads", "0005_alter_ad_category_advcategory"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AdvCategory",
            new_name="AdCategory",
        ),
        migrations.AlterModelOptions(
            name="ad",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Объявление",
                "verbose_name_plural": "Объявления",
            },
        ),
        migrations.RemoveField(
            model_name="ad",
            name="category",
        ),
    ]
