from django.contrib import admin
from .import models
from .models import Payment_detail
from .models import CinemaHall
from .models import Seat
from .models import Booking
# Register your models here.

admin.site.register(CinemaHall)
admin.site.register(Seat)
admin.site.register(Booking)
admin.site.register(Payment_detail)
