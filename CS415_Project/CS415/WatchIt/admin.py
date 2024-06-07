import csv
from datetime import datetime
from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from .forms import MovieForm, ShowtimeForm

from .views import booking_report_view
from .models import Booking, CinemaHall, Feedback, Showtime
from .utils import get_sales_report
from . import models
from django.utils.html import format_html

from django.core.mail import send_mail

import logging

from django.urls import path
from .models import Booking
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os
from xhtml2pdf import pisa
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import make_aware

admin.site.site_header = "WatchIt Administration"
admin.site.site_title = "WatchIt Admin"
admin.site.index_title = "Welcome to the WatchIt Admin Panel"


class MovieAdmin(admin.ModelAdmin):
    form = MovieForm
    list_display = ('title', 'release_date', 'duration', 'thumbnail', 'director')
    search_fields = ('title', 'director')
    list_filter = ('release_date', 'tags')
    fields = ('title', 'description', 'duration', 'starring', 'director', 'release_date', 'language', 'ageRating', 'image', 'trailer', 'tags')
    
    def thumbnail(self, obj):
        return format_html('<img src="{}" width="150" height="100" />', obj.image.url)
    thumbnail.short_description = 'Image'


class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats')
    search_fields = ('user__username', 'movie__title')
    list_filter = ('booking_date', 'showtime')
    fields = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats', 'seats', 'edited')
    readonly_fields = ('booking_date',)
    filter_horizontal = ('seats',)

class SeatInline(admin.TabularInline):
    model = models.Seat
    extra = 0
    readonly_fields = ('seat_label', 'availability')
    can_delete = False




class ShowtimeAdmin(admin.ModelAdmin):
    form = ShowtimeForm
    list_display = ('movie_thumbnail', 'movie', 'cinema_hall_type', 'local_showtime')
    search_fields = ('movie__title', 'cinema_hall__cinema_type')
    list_filter = ('showtime',)
    inlines = [SeatInline]
    change_form_template = 'admin/WatchIt/Showtime/change_form.html'

    def movie_thumbnail(self, obj):
        if obj.movie and obj.movie.image:
            return format_html('<img src="{}" width="100" height="75" />', obj.movie.image.url)
        return "No Image"
    movie_thumbnail.short_description = 'Movie Thumbnail'

    def cinema_hall_type(self, obj):
        return obj.cinema_hall.cinema_type
    cinema_hall_type.short_description = 'Cinema Type'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:object_id>/delete/',
                self.admin_site.admin_view(self.delete_view),
                name='delete_showtime',
            ),
        ]
        return custom_urls + urls

    def delete_view(self, request, object_id, extra_context=None):
        showtime = get_object_or_404(models.Showtime, pk=object_id)
        if not request.user.is_superuser:
            return HttpResponseForbidden("You don't have permission to delete this showtime.")
        showtime.seats.all().delete()
        showtime.delete()
        return redirect('admin/WatchIt/Showtime/change_form.html')




class SeatAdmin(admin.ModelAdmin):
    list_display = ('seat_label', 'showtime', 'availability')
    search_fields = ('seat_label', 'showtime__movie__title')
    list_filter = ('availability', 'showtime')
    readonly_fields = ('seat_label', 'showtime')
    list_select_related = ('showtime',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        showtime_id = request.GET.get('showtime__id__exact')
        if showtime_id:
            queryset = queryset.filter(showtime__id=showtime_id)
        return queryset

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
        
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats', 'get_seat_labels')
    search_fields = ('user__username', 'movie__title')
    list_filter = ('booking_date', 'showtime')
    fields = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats', 'adults', 'children', 'seats', 'edited')
    readonly_fields = ('booking_date',)
    filter_horizontal = ('seats',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('booking_report/', self.admin_site.admin_view(booking_report_view), name='booking-report'),
        ]
        return custom_urls + urls

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'created_at', 'approved', 'reviewed')
    list_filter = ('approved', 'reviewed')
    search_fields = ('subject', 'feedback')


admin.site.register(models.CinemaHall)
admin.site.register(models.Seat, SeatAdmin)
admin.site.register(models.Movie, MovieAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Booking, BookingAdmin)
admin.site.register(models.Showtime, ShowtimeAdmin)
admin.site.register(models.Deals)
admin.site.register(models.User)

admin.site.register(models.Feedback, FeedbackAdmin)




