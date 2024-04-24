from django.contrib import admin
from .import models

from .models import Movie
from .models import Tag
from .models import CinemaHall
from .models import Seat
from .models import Booking
# Register your models here.




# Register your models here.

admin.site.register(models.CinemaHall)
admin.site.register(models.Seat)
admin.site.register(models.Movie)
admin.site.register(models.Tag)
admin.site.register(models.Booking)


