# Generated by Django 5.0.6 on 2024-05-19 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WatchIt', '0040_movie_director'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]