
import logging

import csv

import os
import json
import re
import random
import secrets
import threading
import stripe
import pytz
import qrcode
import base64
from io import BytesIO
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib import messages
from venv import logger
from django.shortcuts import get_object_or_404, render, redirect
import pyotp
from xhtml2pdf import pisa
from .models import User
from django.utils import timezone
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from django.db.models.functions import TruncMinute
from django.db.models import Count, Sum
from django.db.models.functions import Cast
from django.db.models import FloatField
from django.template.loader import get_template
import os
from datetime import timedelta
from reportlab.lib.pagesizes import landscape, A4
import secrets
import qrcode
import random
from io import BytesIO
import base64
from django.contrib import messages
from validate_email import validate_email
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.utils.safestring import mark_safe
from helpers.decorators import auth_user_should_not_access
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .utils import generate_token
from django.core.mail import EmailMessage
import threading
from urllib.parse import urlencode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .models import PasswordResetToken
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa  
from decimal import Decimal
from django.utils import timezone
token_generator = PasswordResetTokenGenerator()

logger = logging.getLogger('WatchIt.security')


from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .models import Feedback, User, Seat, Booking, CinemaHall, Movie, Tag, Showtime, Deals, PasswordResetToken

from .models import User, Seat, Booking, CinemaHall, Movie, Tag, Showtime, Deals, PasswordResetToken
from .recommend import get_recommendations
from .utils import generate_token
from validate_email import validate_email
from urllib.parse import urlencode
from helpers.decorators import auth_user_should_not_access
import matplotlib.pyplot as plt
from django.http import HttpResponse
from io import BytesIO
from .utils import get_user_activity_report, get_sales_report
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.functions import TruncMinute
from django.db.models import Count, Sum
from django.db.models.functions import Cast
from django.db.models import FloatField
from django.template.loader import get_template
from xhtml2pdf import pisa
from .forms import FeedbackForm  



# Initialize stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

# Token generator for password reset
token_generator = PasswordResetTokenGenerator()

from django.utils.timezone import make_aware
from .utils import generate_excel  # Import the utility function


def booking_report_view(request):
    queryset = Booking.objects.all()

    # Apply filters
    booking_date = request.GET.get('booking_date')
    cinema_hall_id = request.GET.get('cinema_hall')
    user = request.GET.get('user')

    if booking_date:
        try:
            date_obj = datetime.strptime(booking_date, '%Y-%m-%d')
            date_obj = make_aware(date_obj)  # Make the datetime object timezone-aware
            queryset = queryset.filter(booking_date=date_obj)
        except ValueError:
            # Handle incorrect date format
            return HttpResponse('Invalid date format. Please use YYYY-MM-DD.')

    if cinema_hall_id:
        queryset = queryset.filter(cinema_hall__id=cinema_hall_id)
    if user:
        queryset = queryset.filter(user__username__icontains=user)

    total_amount = sum(booking.payment_amount for booking in queryset)

    # Handle Excel download
    if request.GET.get('download') == 'excel':
        return generate_excel(queryset)

    return render(request, 'admin/booking_report.html', {
        'bookings': queryset,
        'cinema_halls': CinemaHall.objects.all(),
        'total_amount': total_amount,
    })


def admin_dashboard(request):
    total_bookings = Booking.objects.count()

    # Fetch minute-wise sales and convert Decimal to float for JavaScript compatibility
    minute_sales = (Booking.objects
                     .annotate(minute=TruncMinute('booking_date'))
                     .values('minute')
                     .annotate(total_sales=Sum('payment_amount'))
                     .order_by('minute'))

    minute_sales_data = [[sale['minute'].strftime('%H:%M'), float(sale['total_sales']) if sale['total_sales'] else 0] for sale in minute_sales]

    # Fetch minute-wise user registrations and prepare data
    minute_registrations = (User.objects
                          .annotate(minute=TruncMinute('date_joined'))
                          .values('minute')
                          .annotate(count=Count('id'))
                          .order_by('minute'))

    minute_registrations_data = [[reg['minute'].strftime('%H:%M'), reg['count']] for reg in minute_registrations]

    context = {
        'total_bookings': total_bookings,
        'minute_sales': minute_sales_data,
        'minute_registrations': minute_registrations_data,
    }
    return render(request, 'admin/admin_dashboard.html', context)

def minute_sales(request):
    total_bookings = Booking.objects.count()

    minute_sales = (Booking.objects
                     .annotate(minute=TruncMinute('booking_date'))
                     .values('minute')
                     .annotate(total_sales=Sum('payment_amount'))
                     .order_by('minute'))

    minute_sales_data = [[sale['minute'].strftime('%H:%M'), float(sale['total_sales']) if sale['total_sales'] else 0] for sale in minute_sales]

    context = {
        'total_bookings': total_bookings,
        'minute_sales': minute_sales_data,
    }
    return render(request, 'admin/minute_sales.html', context)

def minute_registrations(request):
    total_bookings = Booking.objects.count()

    minute_registrations = (User.objects
                          .annotate(minute=TruncMinute('date_joined'))
                          .values('minute')
                          .annotate(count=Count('id'))
                          .order_by('minute'))

    minute_registrations_data = [[reg['minute'].strftime('%H:%M'), reg['count']] for reg in minute_registrations]

    context = {
        'total_bookings': total_bookings,
        'minute_registrations': minute_registrations_data,
    }
    return render(request, 'admin/minute_registrations.html', context)

@login_required
def transaction_report(request):
    # Get filter criteria from GET parameters
    movie_id = request.GET.get('movie_id')
    genre_id = request.GET.get('genre_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Initialize query
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')

    # Apply filters
    if movie_id:
        bookings = bookings.filter(movie_id=movie_id)
    if genre_id:
        bookings = bookings.filter(movie__tags__id=genre_id)
    if start_date:
        bookings = bookings.filter(booking_date__gte=datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        bookings = bookings.filter(booking_date__lte=datetime.strptime(end_date, '%Y-%m-%d'))

    # Get all movies and genres for the filter form
    movies = Movie.objects.all()
    genres = Tag.objects.all()

    context = {
        'bookings_with_edit_permission': [(booking, booking.can_edit()) for booking in bookings],
        'movies': movies,
        'genres': genres,
    }

    return render(request, 'your_bookings.html', context)



# views.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from datetime import datetime

@login_required
def transaction_report_pdf(request):
    movie_id = request.GET.get('movie_id')
    genre_id = request.GET.get('genre_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')

    if movie_id:
        bookings = bookings.filter(movie_id=movie_id)
    if genre_id:
        bookings = bookings.filter(movie__tags__id=genre_id)
    if start_date:
        bookings = bookings.filter(booking_date__gte=datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        bookings = bookings.filter(booking_date__lte=datetime.strptime(end_date, '%Y-%m-%d'))

    total_amount = sum(booking.payment_amount for booking in bookings)
    booking_list = []

    for booking in bookings:
        seat_labels = ', '.join(seat.seat_label for seat in booking.seats.all())
        showtime = booking.showtime.showtime if booking.showtime else 'N/A'
        card_details = f"**** **** **** {booking.card_last4}" if booking.card_last4 else 'N/A'
        booking_list.append({
            'cinema_hall': booking.cinema_hall.cinema_type if booking.cinema_hall else 'N/A',
            'movie': booking.movie.title if booking.movie else 'N/A',
            'showtime': showtime,
            'seat_labels': seat_labels,
            'payment_amount': booking.payment_amount,
            'booking_date': booking.booking_date.strftime('%Y-%m-%d %H:%M:%S') if booking.booking_date else 'N/A',
            'card_details': card_details
        })

    context = {
        'user': request.user.username if request.user else 'N/A',
        'total_amount': f"{total_amount:.2f}",
        'bookings': booking_list,
        'image_url': None
    }

    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, 'movie_images', 'WIT.jpg')
        if os.path.exists(image_path):
            context['image_url'] = image_path
    except Exception as e:
        print(f"Error loading logo: {e}")

    template = get_template('transaction_report.html')
    html = template.render(context)
    result = BytesIO()

    pisa_status = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=result)

    if pisa_status.err:
        return HttpResponse('We had some errors with code %s' % pisa_status.err)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transaction_report.pdf"'
    return response

  
def Home(request):
    today = timezone.now().date()
    movies = Movie.objects.filter(release_date__lte=today)  # Fetch movies with release_date today or in the past
    deals = Deals.objects.all()
    movies_chunks = [movies[i:i+3] for i in range(0, len(movies), 3)]
    return render(request, 'Home.html', {'movies': movies, 'movies_chunks': movies_chunks, 'deals': deals,})

@login_required
def Loggedin(request):
    
    return render(request, 'LoggedIn.html')

def LogoutUser(request):
    logout(request)
    messages.success(request, 'Logged out Successfully')
    return redirect('Home')

def display_hall(request, cinema_hall_id, movie_id, showtime_id):
    
    showtime = get_object_or_404(Showtime, cinema_hall_id=cinema_hall_id, movie_id=movie_id, id=showtime_id)

    seats = showtime.seats.all().order_by('id')
    # Custom alphanumeric sorting
    def alphanum_key(seat):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', seat.seat_label)]
    seats = sorted(seats, key=alphanum_key)

    # Retrieve ticket counts from session
    adult_tickets = request.session.get('adult_tickets', 0)
    child_tickets = request.session.get('child_tickets', 0)
    total_tickets = adult_tickets + child_tickets

    print("Adult Tickets: ", adult_tickets)
    print("Child Tickets: ", child_tickets)
    print("Total Tickets: ", total_tickets)


    return render(request, 'cinema.html', {
        'cinema_hall': showtime.cinema_hall,
        'movie': showtime.movie,
        'seats': seats,
        'total_tickets': total_tickets,
        'showtime': showtime,
    })

from datetime import datetime
from django.utils import timezone
from .models import Tag, Movie, Showtime
from django.shortcuts import render

def movie_list(request):
    tags = Tag.objects.all()
    selected_tag_name = request.GET.get("tag")
    
    if selected_tag_name:
        movies = Movie.objects.filter(tags__name=selected_tag_name).distinct()
    else:
        movies = Movie.objects.all()
    
    now = timezone.now().date()
    
    # Get distinct show dates for movies currently showing
    show_dates = Showtime.objects.filter(movie__in=movies, showtime__gte=now).values_list('showtime__date', flat=True).distinct()
    show_dates = sorted(show_dates)
    
    selected_date = request.GET.get("show_date")
    formatted_date = None

    if selected_date:
        # Convert the selected_date from "May 28, 2024" format to "YYYY-MM-DD" format
        formatted_date = datetime.strptime(selected_date, "%B %d, %Y").strftime("%Y-%m-%d")
    
    if formatted_date:
        # Use the formatted_date in your queryset only if it's not None
        movies = Movie.objects.filter(showtimes__showtime__date=formatted_date).distinct()
    else:
        movies = Movie.objects.all()

    return render(request, 'movie_list.html', {
        'movies': movies,
        'now': now,
        'tags': tags,
        'selected_tag_name': selected_tag_name,
        'show_dates': show_dates
    })

from collections import defaultdict
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from .models import Movie, Showtime




def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    showtimes_by_date = defaultdict(list)
    show_dates = set()
    
    # Grouping showtimes by date and collecting unique show dates
    for showtime in movie.showtimes.filter(showtime__gt=timezone.now()).order_by('showtime'):
        showtime_date = showtime.showtime.date()
        showtimes_by_date[showtime_date].append(showtime)
        show_dates.add(showtime_date)

    selected_date_str = request.GET.get('date', None)
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = min(show_dates, default=None)
    else:
        selected_date = min(show_dates, default=None)
    
    context = {
        'movie': movie,
        'showtimes_by_date': dict(showtimes_by_date),
        'show_dates': sorted(show_dates),
        'selected_date': selected_date,
        'showtimes': showtimes_by_date[selected_date] if selected_date in showtimes_by_date else None
    }
    return render(request, 'movie_detail.html', context)

from django.http import JsonResponse



def movie_showtimes(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    selected_date_str = request.GET.get('date', None)
    
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)
    else:
        return JsonResponse({'error': 'No date provided'}, status=400)
    
    showtimes = movie.showtimes.filter(showtime__date=selected_date, showtime__gt=timezone.now()).order_by('showtime')
    showtime_list = [
        {
            'id': showtime.id,
            'showtime': showtime.showtime.isoformat(),
            'cinema_hall_id': showtime.cinema_hall.id,
            'movie_id': movie.id
        }
        for showtime in showtimes
    ]
    
    return JsonResponse({'showtimes': showtime_list})



from django.http import JsonResponse

def movie_showtimes(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    selected_date_str = request.GET.get('date', None)
    
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)
    else:
        return JsonResponse({'error': 'No date provided'}, status=400)
    
    showtimes = movie.showtimes.filter(showtime__date=selected_date, showtime__gt=timezone.now()).order_by('showtime')
    showtime_list = [
        {
            'id': showtime.id,
            'showtime': showtime.showtime.isoformat(),
            'cinema_hall_id': showtime.cinema_hall.id,
            'movie_id': movie.id
        }
        for showtime in showtimes
    ]
    
    return JsonResponse({'showtimes': showtime_list})


def redirect_to_payment(request, cinema_hall_id):
    selected_seat_ids = request.POST.getlist('seats[]')
    request.session['selected_seats'] = selected_seat_ids  # Storing selected seats in session
    # Use reverse to get the URL for the 'payment' view and append the seat IDs as query parameters
    payment_url = reverse('payment', args=[cinema_hall_id]) + '?seats=' + ','.join(selected_seat_ids)
    return HttpResponseRedirect(payment_url)

@require_POST
@csrf_exempt  # Consider using csrf_protect if possible for security
def save_total_price_to_session(request):
    request.session['total_price'] = request.POST.get('total_price')
    return JsonResponse({'success': True})

  
from django.shortcuts import get_object_or_404, render, redirect


def selectTickets(request, cinema_hall_id, movie_id, showtime_id):
    cinema_hall = get_object_or_404(CinemaHall, id=cinema_hall_id)
    movie = get_object_or_404(Movie, id=movie_id)
    show = get_object_or_404(Showtime, id=showtime_id)
    
    print("Cinema Hall ID:", cinema_hall_id)
    print("Movie ID:", movie_id)
    print("Showtime ID:", show)

    is_wednesday = show.showtime.weekday() == 2

    if request.method == 'POST':
        adult_tickets = int(request.POST.get('adult_quantity', 0))
        child_tickets = int(request.POST.get('child_quantity', 0))
        adult_price = cinema_hall.adult_price
        child_price = cinema_hall.child_price
        
        total_tickets = adult_tickets + child_tickets

        if is_wednesday:
            total_amount = (Decimal(adult_tickets) * (adult_price/2)) + (Decimal(child_tickets) * (child_price/2))
            
        else:
            total_amount = (Decimal(adult_tickets) * adult_price) + (Decimal(child_tickets) * child_price)

        
        if total_tickets == 0:
            message = "Please select at least one ticket before proceeding."
            return render(request, 'selectTickets.html', {
                'message': message, 
                'cinema_hall': cinema_hall,
                'movie': movie,
                'show': show,
                'is_wednesday': is_wednesday
            })
        else:
            request.session['adult_tickets'] = adult_tickets
            request.session['child_tickets'] = child_tickets
            request.session['total_price'] = float(total_amount)
            request.session['total_tickets'] = total_tickets

            return redirect('display_hall', cinema_hall_id=cinema_hall_id, movie_id=movie_id, showtime_id=showtime_id)

    return render(request, 'selectTickets.html', {
        'cinema_hall': cinema_hall,
        'movie': movie,
        'show': show,
        'is_wednesday': is_wednesday,
        'half_adult_price': cinema_hall.adult_price/2,
        'half_child_price': cinema_hall.child_price/2,
    })

def payment(request, cinema_hall_id):
    movie_id = request.GET.get('movie_id')
    showtime_id = request.GET.get('showtime_id')
    selected_seat_ids = request.GET.get('seats', '').split(',')
    total_price = request.session.get('total_price', 0)
    total_tickets = int(request.GET.get('total_tickets', 0))
    
    cinema_hall = get_object_or_404(CinemaHall, id=cinema_hall_id)
    movie = get_object_or_404(Movie, id=movie_id)
    show = get_object_or_404(Showtime, id=showtime_id)
    seats = Seat.objects.filter(id__in=selected_seat_ids)

    # Add a print statement to debug if the stripe public key is being passed
    print(f"Stripe Public Key: {settings.STRIPE_PUBLIC_KEY}")

    return render(request, 'payment.html', {
        'cinema_type': cinema_hall.cinema_type,
        'movie_title': movie.title,
        'movie_id': movie_id,
        'cinema_hall_id': cinema_hall_id,
        'movie_duration': movie.duration,
        'total_price': total_price,
        'total_tickets': total_tickets,
        'selected_seats': seats,
        'show': show,
        'showtime_id': showtime_id,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,  # Pass the Stripe public key to the template
    })


  
@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Data received in process_payment:", data)

            payment_method_id = data.get('payment_method_id')
            cinema_hall_id = data.get('cinema_hall_id')
            movie_id = data.get('movie_id')
            showtime_id = data.get('showtime_id')
            total_price = data.get('total_price')
            total_tickets = data.get('total_tickets')
            selected_seat_ids = data.get('seats', [])

            print(f"Payment Method ID: {payment_method_id}")
            print(f"Cinema Hall ID: {cinema_hall_id}")
            print(f"Movie ID: {movie_id}")
            print(f"Showtime ID: {showtime_id}")
            print(f"Total Price: {total_price}")
            print(f"Total Tickets: {total_tickets}")
            print(f"Selected Seat IDs: {selected_seat_ids}")

            total_price_cents = int(float(total_price) * 100)

            # Step 1: Create the PaymentIntent without the confirmation_method parameter
            payment_intent = stripe.PaymentIntent.create(
                amount=total_price_cents,
                currency='usd',
                payment_method=payment_method_id,
                automatic_payment_methods={
                    'enabled': True,
                    'allow_redirects': 'never'
                }
            )

            # Step 2: Manually confirm the PaymentIntent
            stripe.PaymentIntent.confirm(
                payment_intent.id,
                payment_method=payment_method_id
            )

             # Retrieve card details
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            card_last4 = payment_method.card.last4 if payment_method and payment_method.card else ''


            with transaction.atomic():
                cinema_hall = CinemaHall.objects.get(id=cinema_hall_id)
                movie = Movie.objects.get(id=movie_id)
                showtime = Showtime.objects.get(id=showtime_id)
                seats = Seat.objects.filter(id__in=selected_seat_ids, availability=True)

                if seats.count() != len(selected_seat_ids):
                    print("Seat availability error")
                    return JsonResponse({'success': False, 'error': 'One or more seats are no longer available.'})

                booking = Booking.objects.create(
                    cinema_hall=cinema_hall,
                    movie=movie,
                    payment_amount=total_price,
                    showtime=showtime,
                    num_seats=total_tickets,
                    charge_id=payment_intent.id,  # Store the PaymentIntent ID
                    card_last4=card_last4
                )
                if request.user.is_authenticated:
                    booking.user = request.user
                booking.seats.set(seats)
                booking.save()
                seats.update(availability=False)

                return JsonResponse({'success': True})
        except stripe.error.CardError as e:
            print(f"Stripe error: {str(e.user_message)}")
            return JsonResponse({'success': False, 'error': str(e.user_message)})
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    print("Invalid request method")
    return JsonResponse({'error': 'Invalid request method'})

def booking_success(request):
    request.session.flush()
    return render(request, 'booking_success.html')


def generate_purchase_history(request, booking_id):
    # Get the booking instance
    booking = get_object_or_404(Booking, id=booking_id)

    # Fetch the related showtime
    showtime_instance = Showtime.objects.filter(movie=booking.movie, cinema_hall=booking.cinema_hall).first()
    showtime = showtime_instance.showtime.strftime("%Y-%m-%d %H:%M:%S") if showtime_instance else "N/A"

    # Get the booked movie image URL
    booked_movie_image_url = request.build_absolute_uri(booking.movie.image.url) if booking.movie.image else None

    # Fetch some random movies for the images, excluding the booked movie
    now_showing_movies = Movie.objects.filter(
        release_date__lte=timezone.now()
            ).exclude(
                id=booking.movie.id
            ).order_by('?')[:3]

    # Get absolute URL for image
    for movie in now_showing_movies:
        movie.image_url = request.build_absolute_uri(movie.image.url) if movie.image else None

    # Render HTML template with context
    html = render_to_string('generating_pdf.html', {
        'booking': booking,
        'showtime': showtime,
        'booked_movie_image_url': booked_movie_image_url,
        'now_showing_movies': now_showing_movies
    })

    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="purchase_history_{booking.id}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Return PDF response
    if pisa_status.err:
        return HttpResponse('We had some errors<pre>' + html + '</pre>')
    return response


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def movie_recommendations(request):
    recommended_movies = get_recommendations(request.user)
    return render(request, 'recommendations.html', {
        'recommended_movies': recommended_movies,
    })

@login_required
def your_bookings(request):
    current_time = timezone.localtime(timezone.now())
    your_bookings = Booking.objects.filter(user=request.user, showtime__showtime__gt=current_time).select_related('movie', 'cinema_hall', 'showtime')
    

    bookings_with_edit_permission = []
    for booking in your_bookings:
        # Check if the booking was made for a Wednesday show
        is_wednesday_show = booking.showtime.showtime.weekday() == 2
        can_edit = not (booking.edited or is_wednesday_show) and current_time <= booking.showtime.showtime - timedelta(hours=2)
        bookings_with_edit_permission.append((booking, can_edit))

    return render(request, 'your_bookings.html', {'bookings_with_edit_permission': bookings_with_edit_permission})

@login_required
def list_purchase_history(request):
    # Fetch bookings where showtime is in the past
    current_time = timezone.localtime(timezone.now())
    purchase_histories = Booking.objects.filter(user=request.user, showtime__showtime__lte=current_time).select_related('movie', 'cinema_hall', 'showtime')
    return render(request, 'purchase_history.html', {'purchase_histories': purchase_histories})

@login_required
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Disallow editing if booking is for a Wednesday show
    if booking.edited or booking.showtime.showtime.weekday() == 2 or timezone.now() > booking.showtime.showtime - timedelta(hours=2):
        return redirect('your_bookings')

    today = timezone.now().date()
    movies = Movie.objects.filter(release_date__lte=today)

    if request.method == 'POST':
        selected_movie_id = request.POST.get('movie_id')
        return redirect('edit_showtime', booking_id=booking.id, movie_id=selected_movie_id, cinema_hall_id=booking.cinema_hall.id)

    return render(request, 'edit_booking.html', {
        'booking': booking,
        'movies': movies,
    })

@login_required
def edit_showtime(request, booking_id, movie_id, cinema_hall_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.edited or timezone.now() > booking.showtime.showtime - timedelta(hours=2):
        return redirect('your_bookings')

    movie = get_object_or_404(Movie, id=movie_id)
    cinema_hall = get_object_or_404(CinemaHall, id=cinema_hall_id)
    showtimes = Showtime.objects.filter(movie=movie, cinema_hall=cinema_hall, showtime__gt=timezone.now())

    if request.method == 'POST':
        selected_showtime_id = request.POST.get('showtime_id')
        return redirect('edit_seats', booking_id=booking_id, showtime_id=selected_showtime_id, cinema_hall_id=cinema_hall_id)

    return render(request, 'edit_showtime.html', {
        'movie': movie,
        'showtimes': showtimes,
        'cinema_hall': cinema_hall,
    })

@login_required
def edit_seats(request, booking_id, showtime_id, cinema_hall_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.edited or timezone.now() > booking.showtime.showtime - timedelta(hours=2):
        return redirect('your_bookings')

    showtime = get_object_or_404(Showtime, id=showtime_id, cinema_hall_id=cinema_hall_id)
    seats = showtime.seats.all().order_by('id')

    if request.method == 'POST':
        selected_seat_ids = request.POST.getlist('seats[]')
        if len(selected_seat_ids) != booking.num_seats:
            message = f"You must select exactly {booking.num_seats} seats."
            return render(request, 'edit_seats.html', {
                'showtime': showtime,
                'seats': seats,
                'message': message,
                'num_seats': booking.num_seats,
                'cinema_hall': showtime.cinema_hall,
            })
        return redirect('confirm_edit_booking', booking_id=booking_id, showtime_id=showtime_id, seats=','.join(selected_seat_ids))

    return render(request, 'edit_seats.html', {
        'showtime': showtime,
        'seats': seats,
        'num_seats': booking.num_seats,
        'cinema_hall': showtime.cinema_hall,
    })


@login_required
def confirm_edit_booking(request, booking_id, showtime_id, seats):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.edited or timezone.now() > booking.showtime.showtime - timedelta(hours=2):
        return redirect('your_bookings')

    showtime = get_object_or_404(Showtime, id=showtime_id, cinema_hall_id=booking.cinema_hall.id)
    seat_ids = seats.split(',')
    selected_seats = Seat.objects.filter(id__in=seat_ids)

    if len(selected_seats) != booking.num_seats:
        return redirect('edit_seats', booking_id=booking_id, showtime_id=showtime_id, cinema_hall_id=booking.cinema_hall.id)

    if request.method == 'POST':
        with transaction.atomic():
            previous_seats = booking.seats.all()
            previous_seats.update(availability=True)
            booking.showtime = showtime
            booking.movie = showtime.movie
            booking.seats.set(selected_seats)
            booking.edited = True  # Mark the booking as edited
            booking.save()
            selected_seats.update(availability=False)

        return redirect('your_bookings')

    return render(request, 'confirm_edit_booking.html', {
        'booking': booking,
        'showtime': showtime,
        'seats': selected_seats,
    })


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

def send_activation_email(user, request):

    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    email_body = render_to_string('activate.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user),
    })
    
    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=settings.EMAIL_FROM_USER,
                         to=[user.email]
                         )

    if not settings.TESTING:
        EmailThread(email).start()

def send_otp(request, user):
    current_site = get_current_site(request)
    email_subject = 'One-Time Password'
    
    # Generate a random 6-digit OTP
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    email_body = render_to_string('otp_email.html', {
        'user': user,
        'domain': current_site.domain,
        'otp': otp,
    })
    
    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=settings.EMAIL_FROM_USER,
                         to=[user.email])

    if not settings.TESTING:
        EmailThread(email).start()
    
    # Store OTP and user ID in session for verification
    logger.info(f" OTP was sent to {user.username}")
    request.session['otp'] = otp
    request.session['pre_otp_user_id'] = user.id

def enter_otp(request):

    if not request.session.get('otp') or not request.session.get('pre_otp_user_id'):
        messages.error(request, 'You need to log in first to receive an OTP.')
        return redirect('Login')
    
    context = {'has_error': False, 'data': request.POST}
    if request.method == 'POST':
        # Get OTP entered by the user from individual input boxes
        entered_otp = ''.join([
            request.POST.get('otp1'),
            request.POST.get('otp2'),
            request.POST.get('otp3'),
            request.POST.get('otp4'),
            request.POST.get('otp5'),
            request.POST.get('otp6'),
        ])
        
        # Retrieve OTP from session
        stored_otp = request.session.get('otp')
        user_id = request.session.get('pre_otp_user_id')
        user = User.objects.get(id=user_id)
        
        if entered_otp == stored_otp:
            login(request, user)
            logger.info(f" {user.username}'s OTP was Verified ")
            return redirect('Home')
        else:
            messages.error(request, 'OTP is Invalid. Please try Again')
            return render(request, 'otp_enter.html')
    
    return render(request, 'otp_enter.html')

def resend_otp(request):
    print("blabla")
    user_id = request.session.get('pre_otp_user_id')
    user = User.objects.get(id=user_id)

    send_otp(request, user)
    messages.success(request, 'New OTP sent successfully!')
    logger.info(f" New OTP sent to {user.username}")
    return redirect('enter_otp')

def Home(request):
    today = timezone.now().date()
    movies = Movie.objects.filter(release_date__lte=today)  # Fetch movies with release_date today or in the past
    deals = Deals.objects.all()
    movies_chunks = [movies[i:i+3] for i in range(0, len(movies), 3)]

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Check if the welcome message has been displayed for this session
        if 'welcome_message_displayed' not in request.session:
            messages.success(request, f'Welcome {request.user.username}!')
            # Set a session variable to indicate that the message has been displayed
            request.session['welcome_message_displayed'] = True

    return render(request, 'Home.html', {'movies': movies, 'movies_chunks': movies_chunks, 'deals': deals})

@auth_user_should_not_access
def SignUp (request):
    if request.method =='POST':
        
        context = {'has_error': False, 'data': request.POST}
        user_fname = request.POST.get('user_fname')
        user_lname = request.POST.get('user_lname')
        user_email = request.POST.get('user_email')
        user_username = request.POST.get('user_username')
        user_pwd = request.POST.get('user_pwd')
        user_phone = request.POST.get('user_phone')

        if len(user_pwd) < 6:
            styled_warning_message = mark_safe('<span style="color: black; font-weight:bold">WARNING</span><br>Password should be at least 6 characters')
            messages.warning(request, styled_warning_message)
            context['has_error'] = True

        if not validate_email(user_email):
            styled_warning_message = mark_safe('<span style="color: black; font-weight:bold">WARNING</span><br>Enter a valid E-mail Address')
            messages.warning(request, styled_warning_message)
            context['has_error'] = True

        if not user_username:
            styled_warning_message = mark_safe('<span style="color: black; font-weight:bold">WARNING</span><br>UserName is Required')
            messages.warning(request, styled_warning_message)
            context['has_error'] = True

        if User.objects.filter(username=user_username).exists():
            styled_warning_message = mark_safe('<span style="color: black; font-weight:bold">WARNING</span><br>Username is taken, choose another one')
            messages.warning(request, styled_warning_message)
            context['has_error'] = True

            return render(request, 'SignUp.html', context, status=409)

        if User.objects.filter(email=user_email).exists():
            styled_warning_message = mark_safe('<span style="color: black; font-weight:bold">WARNING</span><br>E-mail is taken, choose another one')
            messages.warning(request, styled_warning_message)
            context['has_error'] = True

            return render(request, 'SignUp.html', context, status=409)

        if context['has_error']:
            return render(request, 'SignUp.html', context)
        
            # Redirect to login page after successful registration

        user = User.objects.create_user(first_name=user_fname, last_name=user_lname,username=user_username, email= user_email,user_phone=user_phone,password=user_pwd)
        user.save()

        if not context['has_error']:

            send_activation_email(user, request)

            styled_message = mark_safe('<span style="color: black; font-weight:bold">VERIFY</span><br>We sent you an email to verify your account')
            messages.success(request, styled_message)
            logger.info(f"Activation link sent to {user.username}")
            return redirect('Login_first')

            
    return render(request, 'SignUp.html')

def get_login_context(user):
    return {'is_first_login': user.is_first_login}

@auth_user_should_not_access
def Login(request):
    if request.method == 'POST':
        context = {'has_error': False, 'data': request.POST}
        username = request.POST.get('uname')
        password = request.POST.get('pwd')
        otp_method = request.POST.get('otp_method')

        
        # Check if the user exists
        if not User.objects.filter(username=username).exists():
            messages.error(request, "User not found.")
            context['has_error'] = True
            return render(request, 'Login.html', context)
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        print(f'Authenticated User: {user}')
        
        if user is None:
            messages.error(request, "Username or password did not match.")
            context['has_error'] = True
            return render(request, 'Login.html', context)

        if not user.is_email_verified:
            messages.error(request, 'Email is not verified, please check your registered email inbox')
            context['has_error'] = True
            return render(request, 'Login.html', context)

        request.session['pre_otp_user_id'] = user.id  # Save user ID in session

        if user and otp_method == 'via_sms':
            messages.success(request, 'OTP has been sent to your registered phone number')
            return redirect('send_sms')
        
        if user and otp_method  == 'via_email':
            send_otp(request,user)
            messages.success(request, 'OTP has been sent to your registered email')
            return redirect('enter_otp')
        
    return render(request, 'Login.html')

@auth_user_should_not_access
def Login_first(request):
    if request.method == 'POST':
        context = {'has_error': False, 'data': request.POST}
        username = request.POST.get('uname')
        password = request.POST.get('pwd')

        # Check if the user exists
        if not User.objects.filter(username=username).exists():
            messages.error(request, "User not found.")
            context['has_error'] = True
            return render(request, 'Login.html', context)
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        print(f'Authenticated User: {user}')
        
        if user is None:
            messages.error(request, "Username or password did not match.")
            context['has_error'] = True
            return render(request, 'Login.html', context)

        if not user.is_email_verified:
            messages.error(request, 'Email is not verified, please check your registered email inbox')
            context['has_error'] = True
            return render(request, 'Login.html', context)
        
        login(request, user)
        return redirect('Home')
        
    return render(request, 'Login_first_time.html')

def activate_user(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))

        user = User.objects.get(pk=uid)

    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()

        messages.success(request, 'Email verified, you can now login')
        return redirect(reverse('Login_first'))
    messages.error(request, 'Your activation link is not valid.')
    return render(request,'Login_first.html')

def send_resetpassword_email(user, request):

    token = secrets.token_urlsafe(16)  # Generate a unique token
    # Store the token in the user's profile or any other suitable place
    reset_token = PasswordResetToken.objects.create(user=user, token=token)

    current_site = get_current_site(request)
    email_subject = 'Reset your Password'  # Corrected subject
    email_body = render_to_string('reset_pwd.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token,
    })

    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=settings.EMAIL_FROM_USER,
                         to=[user.email])

    if not settings.TESTING:
        EmailThread(email).start()

def forget_password(request):
    if request.method == 'POST':
        username = request.POST.get('uname')

        try:
            user = User.objects.get(username=username)

            if not user.is_email_verified:
                messages.warning(request, 'Email is not verified')
                return redirect('forget_password')

            send_resetpassword_email(user, request)
            messages.success(request, 'Password reset link has been sent to your email')
            return redirect('Login')

        except User.DoesNotExist:
            messages.warning(request, 'Username does not exist')
            return redirect('forget_password')

        except Exception as e:
            print(e)
            messages.error(request, 'An error occurred. Please try again.')
            return redirect('forget_password')

    return render(request, 'forget_password.html')

def reset_password(request, uidb64, token):
    # Validate token
    try:
        user_id = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=user_id)
        reset_token = PasswordResetToken.objects.get(user=user, token=token, used=False)

        # Check if the reset token has expired
        if reset_token.created_at < timezone.now() - timedelta(minutes=1):
            reset_token.delete()  # Delete expired token
            messages.error(request, 'Your password reset link has expired.')
            return redirect('Login')
        
    except (User.DoesNotExist, ValueError, TypeError, PasswordResetToken.DoesNotExist):
        messages.error(request, 'Your Password reset link may have already been used.')
        logger.info(f"User {user.username} changed Password")
        return redirect('Login')

    # Handle password reset form submission
    if request.method == "POST":
        new_password = request.POST.get("pwd")
        confirm_password = request.POST.get("pwd1")
        if new_password and confirm_password and new_password == confirm_password:
                password_pattern = re.compile(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
                )
                if not password_pattern.match(new_password):
                    messages.warning(request, 'Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character.')
                    return redirect('reset_password', uidb64=uidb64, token=token)

                user.set_password(new_password)
                user.save()
                reset_token.used = True
                reset_token.save()
                messages.success(request, 'Your password has been reset. You can now log in.')
                return redirect('Login')
        else:
                messages.warning(request, 'Passwords do not match. Please try again.')
                return redirect('reset_password', uidb64=uidb64, token=token)
    else:
        return render(request, "reset_password_confirm.html")

@login_required
def QRcode(request):
    # Generate or retrieve the secret key for the current user
    user = request.user

    #Generate or retrieve the secret key for the current user
    if not user.secret_key:
        user.secret_key = pyotp.random_base32()
        print(user.secret_key)
        user.save()

    secret_key = user.secret_key
    
    # Use the user's email address as the account name
    account_name = user.email
    
    # Optional issuer information
    issuer = "WatchIt"  # Customize the issuer as needed
    
    # Prepare the data for the QR code
    data = {
        'issuer': issuer,
        'secret': secret_key,
        'algorithm': 'SHA1',  # Or use the appropriate algorithm
        'digits': 6,  # Or use the appropriate number of digits
    }
    qr_data = urlencode(data)

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f'otpauth://totp/{account_name}?secret={secret_key}&issuer={issuer}&algorithm=SHA1&digits=6')
    qr.make(fit=True)
    
    # Create a BytesIO object to hold the image data
    img_buffer = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(img_buffer, format='PNG')
    
    # Encode the image data as a base64 string
    img_str = base64.b64encode(img_buffer.getvalue()).decode()

    # Pass the base64-encoded image string to the template
    return render(request, 'security.html', {'qr_img': img_str})


@login_required
def enter_otp_app(request):
    if request.method == 'POST':
        # Get the entered OTP from the form
        entered_otp_app = request.POST.get('otp')

        # Retrieve the secret key for the current user
        user = request.user
        secret_key = user.secret_key

        # Verify OTP
        totp = pyotp.TOTP(secret_key)
        current_otp = totp.now()
        current_time = datetime.now()
        print(f"Secret Key: {secret_key}")
        print(f"Current OTP: {current_otp}")
        print(f"Entered OTP: {entered_otp_app}")
        print(f"Current Server Time: {current_time}")

        if totp.verify(entered_otp_app):
            print('OTP successfully verified!')
            messages.success(request, 'OTP successfully verified!')
        else:
            print('oh oh wrong!')
            messages.error(request, 'Invalid OTP. Please try again.')

        return redirect('enter_otp_app')  # Redirect back to the OTP entry page

    return render(request, 'enter_otp_app.html')

from django.shortcuts import render
from django.http import HttpResponse
from .utils import send_sms

def send_test_sms(request):
    user_id = request.session.get('pre_otp_user_id')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
        return redirect('Login')

    phone_number = user.user_phone

    if phone_number:
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        message = f'Hi {user.username}! Your verification code for WatchIt App is {otp}'

        try:
            send_sms(phone_number, message)  # Function to send SMS
            # Store OTP and user details in the session
            request.session['otp'] = otp
            return redirect('verify_otp_sms')  # Redirect to OTP verification view
        except Exception as e:
            messages.error(request, f'Failed to send SMS: {e}')
    else:
        messages.error(request, 'Phone number not found.')

    return render(request, 'send_sms.html')

def resend_otp_sms(request):
    user_id = request.session.get('pre_otp_user_id')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
        return redirect('Login')

    phone_number = user.user_phone
    if phone_number:
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        message = f'Hi {user.username}! Your new verification code for WatchIt App is : {otp}'
        try:
            send_sms(phone_number, message)  # Function to send SMS
            # Update OTP in the session
            request.session['otp'] = otp
            messages.success(request, 'New OTP sent successfully!')
            return redirect('verify_otp_sms')  # Redirect to OTP verification view
        except Exception as e:
            messages.error(request, f'Failed to send SMS: {e}')
    else:
        messages.error(request, 'Phone number not found.')

    return render(request, 'send_sms.html')

def verify_otp_sms(request):
    if request.method == 'POST':
        entered_otp = ''.join([
            request.POST.get('otp1'),
            request.POST.get('otp2'),
            request.POST.get('otp3'),
            request.POST.get('otp4'),
            request.POST.get('otp5'),
            request.POST.get('otp6'),
        ])

        stored_otp = request.session.get('otp')
        user_id = request.session.get('pre_otp_user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
            return redirect('Login')

        if entered_otp == stored_otp:
            login(request, user)
            # Clear the OTP from the session
            request.session.pop('otp', None)
            request.session.pop('pre_otp_user_id', None)
            return redirect('Home')  # Redirect to a home page or dashboard
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'verify_sms.html')


def LogoutUser(request):
    logout(request)
    messages.success(request, 'Logged out Successfully')
    return redirect('Home')

def user_activity_report_view(request):
    data = get_user_activity_report()
    return render(request, 'reports/user_activity_report.html', {'data': data})

def sales_report_view(request):
    data = get_sales_report()
    return render(request, 'reports/sales_report.html', {'data': data})


def view_log_entries(request):
    log_files = {'activities': 'user_activity.log', 'security': 'security.log'}
    log_entries = {'activities': [], 'security': []}

    for log_type, log_file in log_files.items():
        log_file_path = os.path.join(settings.BASE_DIR, 'logs', log_file)
        with open(log_file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(' ')  # Split log entry into parts
                timestamp = ' '.join(parts[:2])  # Extract timestamp
                level = parts[2]  # Extract log level
                message = ' '.join(parts[3:])  # Extract log message
                log_entry = {'timestamp': timestamp, 'level': level, 'message': message}
                log_entries[log_type].append(log_entry)  # Add log entry to respective list

    # Pass log entries to template context
    context = {'log_entries': log_entries}
    return render(request, 'admin/user_activity.html', context)


def is_admin(user):
    return user.is_superuser


@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Feedback successfully submitted!')
            return redirect('my_feedback')  # Redirect to 'user_feedback_list'
        else:
            print(form.errors)  # Print form errors to the console
            messages.error(request, 'Please correct the error below.')
    else:
        form = FeedbackForm()
    return render(request, 'Feedback.html', {'form': form})

def my_feedback(request):
    feedbacks = Feedback.objects.filter(user=request.user)
    return render(request, 'my_feedback.html', {'feedbacks': feedbacks})

def feedback_list(request):
    feedbacks = submit_feedback.objects.filter(reviewed=False)  # Show only unreviewed feedback
    return render(request, 'feedback_list.html', {'feedbacks': feedbacks})

  
@login_required
@user_passes_test(is_admin)
def approve_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.approved = True
    feedback.reviewed = True
    feedback.save()
    messages.success(request, 'Feedback approved successfully!')
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def reject_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.approved = False
    feedback.reviewed = True
    feedback.save()
    messages.success(request, 'Feedback rejected successfully!')
    return redirect('admin_dashboard')

  
def admin_dashboard(request):
    total_bookings = Booking.objects.count()

    # Fetch minute-wise sales and convert Decimal to float for JavaScript compatibility
    minute_sales = (Booking.objects
                     .annotate(minute=TruncMinute('booking_date'))
                     .values('minute')
                     .annotate(total_sales=Sum('payment_amount'))
                     .order_by('minute'))

    minute_sales_data = [[sale['minute'].strftime('%H:%M'), float(sale['total_sales']) if sale['total_sales'] else 0] for sale in minute_sales]

    # Fetch minute-wise user registrations and prepare data
    minute_registrations = (User.objects
                          .annotate(minute=TruncMinute('date_joined'))
                          .values('minute')
                          .annotate(count=Count('id'))
                          .order_by('minute'))

    minute_registrations_data = [[reg['minute'].strftime('%H:%M'), reg['count']] for reg in minute_registrations]

    context = {
        'total_bookings': total_bookings,
        'minute_sales': minute_sales_data,
        'minute_registrations': minute_registrations_data,
    }
    return render(request, 'admin/admin_dashboard.html', context)

def minute_sales(request):
    total_bookings = Booking.objects.count()

    minute_sales = (Booking.objects
                     .annotate(minute=TruncMinute('booking_date'))
                     .values('minute')
                     .annotate(total_sales=Sum('payment_amount'))
                     .order_by('minute'))

    minute_sales_data = [[sale['minute'].strftime('%H:%M'), float(sale['total_sales']) if sale['total_sales'] else 0] for sale in minute_sales]

    context = {
        'total_bookings': total_bookings,
        'minute_sales': minute_sales_data,
    }
    return render(request, 'admin/minute_sales.html', context)

def minute_registrations(request):
    total_bookings = Booking.objects.count()

    minute_registrations = (User.objects
                          .annotate(minute=TruncMinute('date_joined'))
                          .values('minute')
                          .annotate(count=Count('id'))
                          .order_by('minute'))

    minute_registrations_data = [[reg['minute'].strftime('%H:%M'), reg['count']] for reg in minute_registrations]

    context = {
        'total_bookings': total_bookings,
        'minute_registrations': minute_registrations_data,
    }
    return render(request, 'admin/minute_registrations.html', context)


