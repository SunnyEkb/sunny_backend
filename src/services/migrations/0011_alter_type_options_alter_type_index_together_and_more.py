# Generated by Django 5.0.4 on 2024-08-01 13:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0010_alter_service_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="type",
            options={
                "ordering": ["parent_id", "id"],
                "verbose_name": "Тип услуги",
                "verbose_name_plural": "Тип услуги",
            },
        ),
        migrations.AlterIndexTogether(
            name="type",
            index_together=set(),
        ),
        migrations.AddField(
            model_name="type",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="subcategories",
                to="services.type",
                verbose_name="Высшая категория",
            ),
        ),
        migrations.RemoveField(
            model_name="service",
            name="type",
        ),
        migrations.RemoveField(
            model_name="type",
            name="category",
        ),
        migrations.AddField(
            model_name="service",
            name="type",
            field=models.ManyToManyField(
                related_name="types",
                to="services.type",
                verbose_name="Тип услуги",
            ),
        ),
    ]