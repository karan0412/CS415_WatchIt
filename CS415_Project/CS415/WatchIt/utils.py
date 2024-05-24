from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from .models import Booking, User
from django.db.models import Sum, Count


class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk)+six.text_type(timestamp)+six.text_type(user.is_email_verified))


generate_token = TokenGenerator()


def get_user_activity_report():
    # Example: Get user registration counts by date
    data = User.objects.annotate(date_registered=TruncDay('date_joined')).values('date_registered').annotate(count=Count('id')).order_by('date_registered')
    return data

def get_sales_report():
    # Example: Sum of payments received by date
    data = Booking.objects.annotate(date=TruncDay('booking_date')).values('date').annotate(total_sales=Sum('payment_amount')).order_by('date')
    return data