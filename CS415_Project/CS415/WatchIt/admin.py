from datetime import datetime
from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import HttpResponse
from .models import Booking, Showtime
from .utils import get_sales_report
from . import models
from django.utils.html import format_html
from django.urls import path
from .models import Booking
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os
from xhtml2pdf import pisa


admin.site.site_header = "WatchIt Administration"
admin.site.site_title = "WatchIt Admin"
admin.site.index_title = "Welcome to the WatchIt Admin Panel"


class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'thumbnail', 'director')
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
    list_display = ('movie_thumbnail', 'movie', 'cinema_hall_type', 'local_showtime')
    search_fields = ('movie__title', 'cinema_hall__cinema_type')
    list_filter = ('showtime',)
    inlines = [SeatInline]

    def movie_thumbnail(self, obj):
        if obj.movie and obj.movie.image:
            return format_html('<img src="{}" width="100" height="75" />', obj.movie.image.url)
        return "No Image"
    movie_thumbnail.short_description = 'Movie Thumbnail'

    def cinema_hall_type(self, obj):
        return obj.cinema_hall.cinema_type
    cinema_hall_type.short_description = 'Cinema Type'

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
    
# class BookingAdmin(admin.ModelAdmin):
#     list_display = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats')
#     search_fields = ('user__username', 'movie__title')
#     list_filter = ('booking_date', 'showtime')
#     fields = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats', 'seats', 'edited')
#     readonly_fields = ('booking_date',)
#     filter_horizontal = ('seats',)

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('sales_report/', self.admin_site.admin_view(self.sales_report), name='sales-report'),
#         ]
#         return custom_urls + urls

#     def sales_report(self, request):
#         all_sales_report = Booking.objects.all()

#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

#         doc = SimpleDocTemplate(response, pagesize=letter)
#         elements = []

#         # Title
#         title_style = getSampleStyleSheet()['Title']
#         title = Paragraph("Sales Report", style=title_style)
#         elements.append(title)

#         # Sales data headers
#         sales_data = [["Booking Date", "Booking ID", "Movie", "Cinema Hall Type", "Showtime", "Seats", "Payment Amount", "Card Details"]]

#         # Add sales data rows
#         total_amount = 0
#         for booking in all_sales_report:
#             seat_labels = ', '.join(seat.seat_label for seat in booking.seats.all())
#             showtime = booking.showtime.showtime if booking.showtime else 'N/A'
#             card_details = f"**** **** **** {booking.card_last4}" if booking.card_last4 else 'N/A'
#             total_amount += booking.payment_amount
#             sales_data.append([
#                 booking.booking_date.strftime("%Y-%m-%d"),  # Format the date as needed
#                 booking.id,
#                 booking.movie.title,
#                 booking.cinema_hall.cinema_type,
#                 showtime.strftime("%Y-%m-%d %H:%M") if isinstance(showtime, datetime) else showtime,
#                 seat_labels,
#                 f"${booking.payment_amount}",
#                 card_details
#             ])

#         # Create table
#         table = Table(sales_data)
#         table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, 0), 12),
#             ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#             ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#             ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ]))

#         elements.append(table)
#         elements.append(Paragraph(f'Total Amount: ${total_amount:.2f}', title_style))

#         # Build the PDF
#         doc.build(elements)

#         return response


#     def changelist_view(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['custom_button'] = True  # Add custom button to the context
#         return super().changelist_view(request, extra_context=extra_context)

# class BookingAdmin(admin.ModelAdmin):
#     list_display = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats')
#     search_fields = ('user__username', 'movie__title')
#     list_filter = ('booking_date', 'showtime')
#     fields = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats', 'seats', 'edited')
#     readonly_fields = ('booking_date',)
#     filter_horizontal = ('seats',)

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('sales_report/', self.admin_site.admin_view(self.sales_report), name='sales-report'),
#         ]
#         return custom_urls + urls

#     def sales_report(self, request):
#         all_sales_report = Booking.objects.all()
#         total_amount = sum(booking.payment_amount for booking in all_sales_report)

#         for booking in all_sales_report:
#             booking.card_details = f"**** **** **** {booking.card_last4}" if booking.card_last4 else 'N/A'
#             booking.showtime.showtime = booking.showtime.showtime.strftime("%Y-%m-%d %H:%M") if isinstance(booking.showtime.showtime, datetime) else booking.showtime.showtime

#         # Define the path to the logo image
#         base_dir = os.path.dirname(os.path.abspath(__file__))
#         logo_url = os.path.join(base_dir, 'static', 'images', 'WIT.jpg')

#         html_string = render_to_string('sales_report_pdf.html', {
#             'bookings': all_sales_report,
#             'total_amount': total_amount,
#             'logo_url': logo_url,
#         })

#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

#         # Generate PDF
#         pisa_status = pisa.CreatePDF(html_string, dest=response)

#         # Return PDF response
#         if pisa_status.err:
#             return HttpResponse('We had some errors<pre>' + html_string + '</pre>')
#         return response

# class BookingAdmin(admin.ModelAdmin):
#     list_display = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats')
#     search_fields = ('user__username', 'movie__title')
#     list_filter = ('booking_date', 'showtime')
#     fields = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats', 'seats', 'edited')
#     readonly_fields = ('booking_date',)
#     filter_horizontal = ('seats',)

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('sales_report/', self.admin_site.admin_view(self.sales_report), name='sales-report'),
#         ]
#         return custom_urls + urls

#     def sales_report(self, request):
#         all_sales_report = Booking.objects.all()
#         total_amount = sum(booking.payment_amount for booking in all_sales_report)

#         for booking in all_sales_report:
#             booking.card_details = f"**** **** **** {booking.card_last4}" if booking.card_last4 else 'N/A'
#             booking.showtime.showtime = booking.showtime.showtime.strftime("%Y-%m-%d %H:%M") if isinstance(booking.showtime.showtime, datetime) else booking.showtime.showtime

#         html_string = render_to_string('sales_report_pdf.html', {
#             'bookings': all_sales_report,
#             'total_amount': total_amount,
#         })

#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

#         pisa_status = pisa.CreatePDF(
#            html_string, dest=response
#         )

#         if pisa_status.err:
#            return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
#         return response
  
# class BookingAdmin(admin.ModelAdmin):
#     list_display = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats')
#     search_fields = ('user__username', 'movie__title')
#     list_filter = ('booking_date', 'showtime')
#     fields = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats', 'seats', 'edited')
#     readonly_fields = ('booking_date',)
#     filter_horizontal = ('seats',)

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('sales_report/', self.admin_site.admin_view(self.sales_report), name='sales-report'),
#         ]
#         return custom_urls + urls

#     def sales_report(self, request):
#         all_sales_report = Booking.objects.all()
#         total_amount = sum(booking.payment_amount for booking in all_sales_report)

#         for booking in all_sales_report:
#             booking.card_details = f"**** **** **** {booking.card_last4}" if booking.card_last4 else 'N/A'
#             booking.showtime_display = booking.showtime.showtime.strftime("%Y-%m-%d %H:%M") if isinstance(booking.showtime.showtime, datetime) else booking.showtime.showtime
#             booking.seat_labels = ', '.join(seat.seat_label for seat in booking.seats.all())

#         html_string = render_to_string('sales_report_pdf.html', {
#             'bookings': all_sales_report,
#             'total_amount': total_amount,
#         })

#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

#         pisa_status = pisa.CreatePDF(
#            html_string, dest=response
#         )

#         if pisa_status.err:
#            return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
#         return response

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats')
    search_fields = ('user__username', 'movie__title')
    list_filter = ('booking_date', 'showtime')
    fields = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats', 'seats', 'edited')
    readonly_fields = ('booking_date',)
    filter_horizontal = ('seats',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sales_report/', self.admin_site.admin_view(self.sales_report), name='sales-report'),
        ]
        return custom_urls + urls

    def sales_report(self, request):
        all_sales_report = Booking.objects.all()
        total_amount = sum(booking.payment_amount for booking in all_sales_report)

        for booking in all_sales_report:
            booking.card_details = f"**** **** **** {booking.card_last4}" if booking.card_last4 else 'N/A'
            booking.showtime_display = booking.showtime.showtime.strftime("%Y-%m-%d %H:%M") if isinstance(booking.showtime.showtime, datetime) else booking.showtime.showtime
            booking.seat_labels = ', '.join(seat.seat_label for seat in booking.seats.all())

        html_string = render_to_string('sales_report_pdf.html', {
            'bookings': all_sales_report,
            'total_amount': total_amount,
        })

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

        pisa_status = pisa.CreatePDF(
           html_string, dest=response
        )

        if pisa_status.err:
           return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
        return response



admin.site.register(models.CinemaHall)
admin.site.register(models.Seat, SeatAdmin)
admin.site.register(models.Movie, MovieAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Booking, BookingAdmin)
admin.site.register(models.Showtime, ShowtimeAdmin)
admin.site.register(models.Deals)
admin.site.register(models.User)
