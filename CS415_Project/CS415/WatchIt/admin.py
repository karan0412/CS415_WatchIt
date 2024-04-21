from django.contrib import admin
from .import models

from .models import Payment_detail
from .models import CinemaHall
from .models import Seat
from .models import Booking
# Register your models here.

admin.site.register(Payment_detail)


# Register your models here.

admin.site.register(models.CinemaHall)
admin.site.register(models.Seat)
admin.site.register(models.Movies)
admin.site.register(models.Booking)


