# Generated by Django 5.0.6 on 2024-05-22 07:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WatchIt', '0003_remove_discount_end_date_remove_discount_start_date'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Discount',
        ),
    ]