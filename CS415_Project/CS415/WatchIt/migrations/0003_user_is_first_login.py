# Generated by Django 4.2.4 on 2024-05-23 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WatchIt', '0002_user_user_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_first_login',
            field=models.BooleanField(default=True),
        ),
    ]