# Generated by Django 4.2.3 on 2024-04-15 02:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WatchIt', '0007_rename_seat_avail_theatre_availability'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='theatre',
            name='Seat_label',
        ),
    ]