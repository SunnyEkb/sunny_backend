# Generated by Django 5.0.4 on 2024-06-18 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0003_service_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="experience",
            field=models.PositiveIntegerField(default=0, verbose_name="Опыт"),
        ),
        migrations.AddField(
            model_name="service",
            name="place_of_provision",
            field=models.CharField(
                choices=[
                    ("Выезд", "House Call"),
                    ("В офисе", "Office"),
                    ("On line", "On Line"),
                    ("По выбору", "Options"),
                ],
                default="По выбору",
                max_length=50,
                verbose_name="Место оказания услуги",
            ),
        ),
        migrations.AddField(
            model_name="service",
            name="status",
            field=models.IntegerField(
                choices=[
                    (0, "Draft"),
                    (1, "Moderation"),
                    (2, "Published"),
                    (3, "Hidden"),
                    (4, "Cancelled"),
                ],
                default=0,
                verbose_name="Статус услуги",
            ),
        ),
    ]