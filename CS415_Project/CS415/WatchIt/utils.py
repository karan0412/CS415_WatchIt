from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
import openpyxl
from openpyxl.styles import Alignment, Font
from openpyxl.drawing.image import Image
from django.http import HttpResponse
from datetime import datetime
from twilio.rest import Client
from django.conf import settings
from django.db.models.functions import TruncDay
from .models import Booking, User
from django.db.models import Sum, Count
import os

class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk)+six.text_type(timestamp)+six.text_type(user.is_email_verified))


generate_token = TokenGenerator()


def get_twilio_client():
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_sms(to, message):
    client = get_twilio_client()
    message = client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to
    )
    return message.sid


def get_user_activity_report():
    # Example: Get user registration counts by date
    data = User.objects.annotate(date_registered=TruncDay('date_joined')).values('date_registered').annotate(count=Count('id')).order_by('date_registered')
    return data

def get_sales_report():
    # Example: Sum of payments received by date
    data = Booking.objects.annotate(date=TruncDay('booking_date')).values('date').annotate(total_sales=Sum('payment_amount')).order_by('date')
    return data


def generate_excel(queryset):
    # Create a workbook and select the active worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Booking Report"

    # Set the column widths
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 30
    ws.column_dimensions['D'].width = 20
    ws.column_dimensions['E'].width = 20
    ws.column_dimensions['F'].width = 20
    ws.column_dimensions['G'].width = 20
    ws.column_dimensions['H'].width = 30
    ws.column_dimensions['I'].width = 40

    # Add company logo
    logo_path = os.path.join(settings.MEDIA_ROOT, 'movie_images', 'logo.jpg')  # Replace 'logo.jpg' with your logo filename
    if os.path.exists(logo_path):
        logo = Image(logo_path)
        logo.width = 80  # Set the width of the logo
        logo.height = 80  # Set the height of the logo
        ws.add_image(logo, 'A1')
    else:
        ws['A1'] = "Logo not found"
    
    # Merge cells for company details
    ws.merge_cells('B1:E1')
    ws.merge_cells('B2:E2')
    ws.merge_cells('B3:E3')
    ws.merge_cells('B4:E4')
    ws.merge_cells('B5:E5')

    # Add company details
    ws['B1'] = "Company Name: WatchIt"
    ws['B2'] = "Address: 123 Laucala Bay, Suva"
    ws['B3'] = "Phone: +(679) 999-7890"
    ws['B4'] = "Email: info@watchit.com"

    # Add report title
    ws['A6'] = "Booking Report"
    ws['A7'] = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ws['A8'] = ""

    # Add the table headers
    headers = ['ID', 'User', 'Movie', 'Cinema Hall', 'Showtime', 'Booking Date', 'Payment Amount', 'Seats']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=9, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Add the data rows
    row_num = 10
    for booking in queryset:
        booking.seat_labels = ', '.join(seat.seat_label for seat in booking.seats.all())
        showtime_display = booking.showtime.showtime.strftime("%Y-%m-%d %H:%M:%S")  # Format the showtime to a string
        row = [
            booking.id,
            booking.user.username,
            booking.movie.title,
            booking.cinema_hall.cinema_type,
            showtime_display,  # Convert showtime to string
            booking.booking_date.strftime("%Y-%m-%d %H:%M:%S"),  # Convert booking_date to string
            f"${booking.payment_amount:.2f}",
            booking.seat_labels
        ]
        for col_num, value in enumerate(row, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = value
            cell.alignment = Alignment(horizontal="center", vertical="center")
        row_num += 1

    # Save the workbook to a response object
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
    wb.save(response)

    return response