from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from twilio.rest import Client
from django.conf import settings

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

