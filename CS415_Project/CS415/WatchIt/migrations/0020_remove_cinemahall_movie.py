# Generated by Django 4.2.3 on 2024-04-24 06:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WatchIt', '0019_remove_booking_booking_label_remove_movie_tags_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cinemahall',
            name='movie',
        ),
    ]