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


# class Feedback(models.Model):
#     subject = models.CharField(max_length=255)
#     feedback = models.TextField()
#     file = models.FileField(upload_to='feedback_files/', null=True, blank=True)
#     approved = models.BooleanField(default=False)
#     reviewed = models.BooleanField(default=False)

#     def __str__(self):
#         return self.subject

# class Feedback(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     subject = models.CharField(max_length=200)
#     feedback = models.TextField()
#     file = models.FileField(upload_to='feedback_files/', null=True, blank=True)
#     approved = models.BooleanField(default=False)
#     reviewed = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.subject

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

# class CareerApplication(models.Model):
#     name = models.CharField(max_length=255)
#     cv = models.FileField(upload_to='cv_files/')
#     cover_letter = models.FileField(upload_to='cover_letter_files/')
#     approved = models.BooleanField(default=False)
#     reviewed = models.BooleanField(default=False)

#     def __str__(self):
#         return self.name

# class Feedback(models.Model):
#     subject = models.CharField(max_length=255)
#     feedback = models.TextField()
#     file = models.FileField(upload_to='feedback_files/', null=True, blank=True)  # Adjust the `upload_to` path as needed

#     def __str__(self):
#         return self.subject


class User(AbstractUser):
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
        # Convert showtime to the local time
        return timezone.localtime(self.showtime)

    def __str__(self):
        return f"{self.movie.title} at {self.local_showtime()}" 

    def clean(self):
        # Check for overlapping showtimes in the same cinema hall
        end_time = self.showtime + timedelta(minutes=self.movie.duration + 30)
        overlapping_showtimes = Showtime.objects.filter(
            cinema_hall=self.cinema_hall,
            showtime__lt=end_time,
            showtime__gt=self.showtime - timedelta(minutes=self.movie.duration + 30)
        ).exclude(id=self.id)
        if overlapping_showtimes.exists():
            raise ValidationError("There is already a movie scheduled during this time.")

    def save(self, *args, **kwargs):
        self.clean()  # Validating before saving
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    cinema_hall = models.ForeignKey(CinemaHall, related_name='bookings', on_delete=models.CASCADE, null=True, blank=True)
    seats = models.ManyToManyField(Seat, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    movie = models.ForeignKey(Movie, related_name='bookings', on_delete=models.CASCADE, null=True, blank=True)
    showtime = models.ForeignKey(Showtime, related_name='bookings', on_delete=models.CASCADE, null=True, blank=True)
    payment_amount = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    num_seats = models.PositiveIntegerField(default=1)
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


#models.py


class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    used = models.BooleanField(default=False)

    def __str__(self):
        return self.token