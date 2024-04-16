from django.contrib import admin
from .import models

# Register your models here.

admin.site.register(models.CinemaHall)
admin.site.register(models.Seat)
admin.site.register(models.Booking)

