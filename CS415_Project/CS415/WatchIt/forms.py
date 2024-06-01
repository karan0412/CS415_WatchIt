from datetime import timezone
from venv import logger
from django import forms
from .models import CinemaHall, Feedback, Showtime, Movie
from django.utils import timezone


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = '__all__'
        widgets = {
            'release_date': forms.DateInput(attrs={'class': 'datepicker', 'type': 'date'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'feedback', 'file']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'file': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

# class ShowtimeForm(forms.ModelForm):
#     class Meta:
#         model = Showtime
#         fields = ['movie', 'cinema_hall', 'showtime', 'seats_generated']
#         widgets = {
#             'showtime': forms.DateInput(attrs={'class': 'datetimepicker', 'type': 'datetime-local'}),
#         }
    
#     def clean(self):
#         cleaned_data = super().clean()
#         movie = cleaned_data.get("movie")
#         if movie and movie.duration is None:
#             self.add_error('movie', "The selected movie does not have a duration set.")
#         return cleaned_data

class ShowtimeForm(forms.ModelForm):
    showtime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d %H:%M:%S%z']  # Include the expected format with timezone
    )

    class Meta:
        model = Showtime
        fields = ['movie', 'cinema_hall', 'showtime', 'seats_generated']
        widgets = {
            'showtime': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def clean_showtime(self):
        datetime_input = self.cleaned_data.get('showtime')
        # Check if datetime_input is naive or aware
        if datetime_input and timezone.is_naive(datetime_input):
            # Make the datetime timezone-aware
             datetime_with_tz = timezone.make_aware(datetime_input, timezone.get_current_timezone())
        else:
            datetime_with_tz = datetime_input
        return datetime_with_tz