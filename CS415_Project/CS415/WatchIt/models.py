from django.db import models
from django.contrib.auth.models import User
from string import ascii_uppercase
from django.db import models
from django.db import transaction
from django.utils import timezone
from embed_video.fields import EmbedVideoField



class Tag(models.Model):
     name = models.CharField(max_length=100, unique=True)

     def __str__(self):
            return self.name
    
class CinemaHall(models.Model):
    cinema_type = models.CharField(max_length=100, null=True, blank=True)
    num_rows = models.IntegerField(blank=True, null=True)
    num_cols = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.cinema_type} - {self.num_rows}x{self.num_cols} seats"

class Deals (models.Model):
    Meal = models.CharField(max_length=255, null=True, blank=True)
    Price = models.FloatField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='deals_images/', blank=True, null=True)
    def __str__(self):
                return self.Meal
    
                   
class Movie(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    duration = models.IntegerField(help_text="Duration in minutes", null=True, blank=True)
    starring = models.TextField(help_text="Comma-separated list of main actors", null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=100, null=True, blank=True)
    ageRating = models.CharField(max_length=10, null=True, blank=True)
    image = models.ImageField(upload_to='movie_images/', null=True, blank=True)
    trailer = models.URLField(null=True, blank=True) 
    tags = models.ManyToManyField('Tag', related_name='movies')

    def __str__(self):
        return self.title

from django.db import models
from django.utils import timezone

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes', null=True, blank=True)
    cinema_hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, related_name='showtimes')
    showtime = models.DateTimeField()
    seats_generated = models.BooleanField(default=False)

    @property
    def is_future_showtime(self):
        return self.showtime > timezone.now()

    def __str__(self):
        return f"{self.movie.title} at {self.showtime}"

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating and not self.seats_generated:
            self.generate_seats()
            self.seats_generated = True
            super().save(update_fields=['seats_generated'])

    def generate_seats(self):
        # Seat generation logic adapted for Showtime
        seats = []
        for row in range(1, self.cinema_hall.num_rows + 1):
            row_letter = ascii_uppercase[row - 1]
            for col in range(1, self.cinema_hall.num_cols + 1):
                seat_label = f"{row_letter}{col}"
                seats.append(Seat(showtime=self, seat_label=seat_label, availability=True))
        Seat.objects.bulk_create(seats)


class Seat(models.Model):
    showtime = models.ForeignKey(Showtime, related_name='seats', on_delete=models.CASCADE, null=True, blank=True)
    seat_label = models.CharField(max_length=3, null=True, blank=True)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return f"Seat {self.seat_label} in {self.showtime}"


class Booking(models.Model):
    cinema_hall = models.ForeignKey(CinemaHall, related_name='bookings', on_delete=models.CASCADE, null=True, blank=True)
    seats = models.ManyToManyField(Seat, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    movie = models.ForeignKey(Movie, related_name='bookings', on_delete=models.CASCADE, null=True, blank=True)
    payment_amount = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)

    def __str__(self):
        return f"Booking for {self.movie.title} on {self.booking_date}"

    def delete(self, *args, **kwargs):
        # Update seat availability before deleting booking
        seats = self.seats.all()
        seats.update(availability=True)
        super().delete(*args, **kwargs)

