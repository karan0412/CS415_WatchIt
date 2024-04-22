from django.db import models
from django.contrib.auth.models import User
from string import ascii_uppercase
from django.db import models
from django.db import transaction
    
class CinemaHall(models.Model):
    cinema_type = models.CharField(max_length=100, null=True, blank=True)
    num_rows = models.IntegerField(null=True, blank=True)
    num_cols = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Seat.generate_seats(self)


class Seat(models.Model):
    cinema_hall = models.ForeignKey(CinemaHall, related_name='seats', on_delete=models.CASCADE)
    seat_label = models.CharField(max_length=3, null=True, blank=True)
    availability = models.BooleanField(default=True, null=True, blank=True)

    @staticmethod
    def generate_seats(cinema_hall):
        existing_seats = set(cinema_hall.seats.all().values_list('seat_label', flat=True))
        for row in range(1, cinema_hall.num_rows + 1):
            row_letter = ascii_uppercase[row - 1]
            for col in range(1, cinema_hall.num_cols + 1):
                seat_label = f"{row_letter}{col}"
                if seat_label not in existing_seats:
                    Seat.objects.create(cinema_hall=cinema_hall, seat_label=seat_label)

class Tag(models.Model):
     name = models.CharField(max_length=100, unique=True)

     def __str__(self):
            return self.name
   
class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    starring = models.TextField(help_text="Coma-separated list of main actors")
    release_date = models.DateField()
    language = models.CharField(max_length=100)
    ageRating = models.CharField(max_length=10)
    image = models.ImageField(upload_to='movie_images/', blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='movies')
    
    def __str__(self):
                return self.title

class Booking(models.Model):
    seats = models.ManyToManyField(Seat)
    booking_label = models.CharField(max_length=1000, unique=True, null=True, blank=True)
    booking_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            seats = self.seats.all()
            for seat in seats:
                seat.refresh_from_db()  # Ensure the latest data is fetched
                seat.availability = True
                seat.save()
            super().delete(*args, **kwargs)

class Payment_detail(models.Model):
    id= models.AutoField
    payment_Name = models.CharField(null=True)
    payment_amount = models.DecimalField(null=True, decimal_places=2, max_digits=20)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.id)


