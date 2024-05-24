from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

from twilio.rest import Client
from django.conf import settings
from django.db.models.functions import TruncDay
from .models import Booking, User
from django.db.models import Sum, Count


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


