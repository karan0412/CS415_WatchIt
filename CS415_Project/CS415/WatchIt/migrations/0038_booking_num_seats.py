# Generated by Django 5.0.6 on 2024-05-18 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WatchIt', '0037_booking_showtime'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='num_seats',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
