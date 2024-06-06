from venv import logger
from django.db import models
from django.contrib.auth.models import User
from string import ascii_uppercase
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from string import ascii_uppercase
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from string import ascii_uppercase
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import models
from django.utils import timezone


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    feedback = models.TextField()
    file = models.FileField(upload_to='feedback_files/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return self.subject


class User(AbstractUser):
    user_phone = models.CharField(max_length=15, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return self.email

class Tag(models.Model):
     name = models.CharField(max_length=100)

     def __str__(self):
            return self.name
    
class CinemaHall(models.Model):
    cinema_type = models.CharField(max_length=100, null=True, blank=True)
    num_rows = models.IntegerField(blank=True, null=True)
    num_cols = models.IntegerField(blank=True, null=True)
    adult_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    child_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)



    def __str__(self):
        return f"{self.cinema_type} - {self.num_rows}x{self.num_cols} seats"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # After saving, update related showtime seats
        print(f"CinemaHall saved: {self.cinema_type}, {self.num_rows} rows, {self.num_cols} cols")
        showtimes = Showtime.objects.filter(cinema_hall=self)
        for showtime in showtimes:
            print(f"Updating showtime: {showtime.id}")
            showtime.seats_generated = False
            showtime.save()
            print(f"Showtime updated: {showtime.id}")

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
    director = models.TextField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=100, null=True, blank=True)
    ageRating = models.CharField(max_length=10, null=True, blank=True)
    image = models.ImageField(upload_to='movie_images/', null=True, blank=True)
    trailer = models.URLField(null=True, blank=True) 
    tags = models.ManyToManyField(Tag, related_name='movies')

    def __str__(self):
        return self.title


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes', null=True, blank=True)
    cinema_hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, related_name='showtimes')
    showtime = models.DateTimeField()
    seats_generated = models.BooleanField(default=False)

    @property
    def is_future_showtime(self):
        return self.showtime > timezone.now()

    def local_showtime(self):
        return timezone.localtime(self.showtime)

    def __str__(self):
        return f"{self.movie.title} at {self.local_showtime()}" if self.movie else f"Showtime at {self.local_showtime()}"
    
    def clean(self):
        super().clean()

        if not self.showtime:
            raise ValidationError("Showtime must be set.")

        if not self.movie:
            raise ValidationError("A movie must be selected.")
        
        print(f"Cleaning Showtime: {self.showtime}, Movie: {self.movie}")
        if self.movie:
            if self.movie.duration is None:
                raise ValidationError("The selected movie does not have a duration set.")
            end_time = self.showtime + timedelta(minutes=self.movie.duration + 30)
            print(f"Calculated End Time: {end_time}")

            overlapping_showtimes = Showtime.objects.filter(
                cinema_hall=self.cinema_hall,
                showtime__lt=end_time,
                showtime__gte=self.showtime - timedelta(minutes=self.movie.duration + 30)
            ).exclude(pk=self.pk)

            if overlapping_showtimes.exists():
                raise ValidationError("This showtime overlaps with an existing showtime in the same cinema hall.")
        else:
            raise ValidationError("Movie selection is invalid or not provided.")

    def save(self, *args, **kwargs):
        self.clean()  # Validating before saving
        creating = self._state.adding
        if not creating:  # Check if we are updating an existing instance
            old_instance = Showtime.objects.get(pk=self.pk)
            if old_instance.cinema_hall != self.cinema_hall:
                self.seats_generated = False

        super().save(*args, **kwargs)
        
        if not self.seats_generated:
            self.generate_seats()
            self.seats_generated = True
            super().save(update_fields=['seats_generated'])

    def generate_seats(self):
        print(f"Deleting existing seats for showtime {self.id}")
        self.seats.all().delete()  # Clear existing seats to prevent duplication
        seats = []
        for row in range(1, self.cinema_hall.num_rows + 1):
            row_letter = ascii_uppercase[row - 1]
            for col in range(1, self.cinema_hall.num_cols + 1):
                seat_label = f"{row_letter}{col}"
                seats.append(Seat(showtime=self, seat_label=seat_label, availability=True))
        Seat.objects.bulk_create(seats)
        print(f"Generated {len(seats)} seats for showtime {self.id}")


class Seat(models.Model):
    showtime = models.ForeignKey(Showtime, related_name='seats', on_delete=models.CASCADE, null=True, blank=True)
    seat_label = models.CharField(max_length=3, null=True, blank=True)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return f"Seat {self.seat_label} in {self.showtime}"


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    cinema_hall = models.ForeignKey(CinemaHall, related_name='bookings', on_delete=models.CASCADE, null=True, blank=True)
    seats = models.ManyToManyField(Seat, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    movie = models.ForeignKey(Movie, related_name='bookings', on_delete=models.CASCADE, null=True, blank=True)
    showtime = models.ForeignKey(Showtime, related_name='bookings', on_delete=models.CASCADE, null=True, blank=True)
    payment_amount = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    num_seats = models.PositiveIntegerField(default=1)
    adults = models.PositiveIntegerField(null=True, blank=True)
    children = models.PositiveIntegerField(null=True, blank=True)
    edited = models.BooleanField(default=False)
    charge_id = models.CharField(max_length=255, blank=True, null=True)  # Add this line
    card_last4 = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return f"Booking for {self.movie.title} on {self.booking_date}"
    
    def get_seat_labels(self):
        return ", ".join([seat.seat_label for seat in self.seats.all()])

    def delete(self, *args, **kwargs):
        # Update seat availability before deleting booking
        seats = self.seats.all()
        seats.update(availability=True)
        super().delete(*args, **kwargs)



class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    used = models.BooleanField(default=False)

    def __str__(self):
        return self.token
    





