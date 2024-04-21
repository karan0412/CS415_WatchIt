# Generated by Django 5.0.4 on 2024-04-20 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WatchIt', '0011_payment_detail'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('duration', models.IntegerField(help_text='Duration in minutes')),
                ('starring', models.TextField(help_text='Coma-separated list of main actors')),
                ('release_date', models.DateField()),
                ('language', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=100)),
                ('ageRating', models.CharField(max_length=10)),
                ('image', models.ImageField(blank=True, null=True, upload_to='movie_images/')),
            ],
        ),
    ]
