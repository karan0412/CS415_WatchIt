# Generated by Django 4.2.3 on 2024-04-11 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('WatchIt', '0002_delete_anothermodel_delete_samplemodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='CinemaHall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('number_of_seats', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=10)),
                ('is_taken', models.BooleanField(default=False)),
                ('hall', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='WatchIt.cinemahall')),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booked_on', models.DateTimeField(auto_now_add=True)),
                ('seats', models.ManyToManyField(to='WatchIt.seat')),
            ],
        ),
    ]