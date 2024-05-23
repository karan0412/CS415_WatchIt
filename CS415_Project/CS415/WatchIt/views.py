from datetime import datetime
import json
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .models import User
from django.utils import timezone
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import re
from django.http import JsonResponse
from .models import Seat, Booking, CinemaHall, Movie, Tag, Showtime, Deals
from django.http import JsonResponse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.platypus.flowables import HRFlowable, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
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


from .recommend import get_recommendations
#from .forms import BookingForm
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

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

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transaction_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        alignment=TA_CENTER,
        fontSize=24,
        textColor=colors.black
    )
    subtitle_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        alignment=TA_CENTER,
        fontSize=18,
        textColor=colors.black
    )
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['BodyText'],
        fontSize=10,
        leading=12,
        textColor=colors.black
    )
    payment_style = ParagraphStyle(
        'Payment',
        parent=styles['BodyText'],
        fontSize=12,
        leading=14,
        textColor=colors.black,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT
    )
    movie_style = ParagraphStyle(
        'Movie',
        parent=styles['BodyText'],
        fontSize=12,
        leading=14,
        textColor=colors.black,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    small_bold_style = ParagraphStyle(
        'SmallBold',
        parent=styles['BodyText'],
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.black
    )
    terms_style = ParagraphStyle(
        'Terms',
        parent=styles['BodyText'],
        fontSize=8,
        leading=10,
        textColor=colors.black
    )

    def add_background(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.white)
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1)
        footer_text = 'Thank you for your purchase!'
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.black)
        canvas.drawCentredString(doc.pagesize[0] / 2.0, 0.5 * inch, footer_text)
        canvas.restoreState()

    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, 'static', 'logo.jpg')  # Update this path to your logo
        print(f"Checking logo at path: {logo_path}")  # Debug print

        if os.path.exists(logo_path):
            print("Logo found at path")  # Debug print
            logo = Image(logo_path, width=1.5 * inch, height=1.5 * inch)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 12))
        else:
            print("Logo not found at path")  # Debug print
            elements.append(Paragraph("Logo not found.", normal_style))
    except Exception as e:
        print(f"Error loading logo: {e}")  # Debug print
        elements.append(Paragraph("Logo could not be loaded.", normal_style))

    elements.append(Paragraph('Transaction Report', title_style))
    elements.append(Spacer(1, 12))

    # Booking details at the top
    for booking in bookings:
        user = booking.user.username if booking.user else 'N/A'
        elements.append(Paragraph(f'Booking ID: {booking.id}', subtitle_style))
        elements.append(Paragraph(f'User: {user}', subtitle_style))
        elements.append(Spacer(1, 12))
        break  # Only show the first booking details

    data = [['ID', 'Cinema Hall', 'Movie', 'Showtime', 'Seats', 'Payment Amount', 'Booking Date', 'Card Details']]
    total_amount = 0

    for booking in bookings:
        seat_labels = ', '.join(seat.seat_label for seat in booking.seats.all())
        showtime = booking.showtime.showtime if booking.showtime else 'N/A'
        card_details = f"**** **** **** {booking.card_last4}" if booking.card_last4 else 'N/A'
        total_amount += booking.payment_amount
        data.append([
            booking.id,
            booking.cinema_hall.cinema_type if booking.cinema_hall else 'N/A',
            booking.movie.title if booking.movie else 'N/A',
            showtime,
            seat_labels,
            f"${booking.payment_amount}",
            booking.booking_date.strftime('%Y-%m-%d %H:%M:%S') if booking.booking_date else 'N/A',
            card_details
        ])

    elements.append(Paragraph(f'Total Amount: ${total_amount:.2f}', payment_style))
    elements.append(Spacer(1, 12))

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFD700')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))

    elements.append(KeepTogether([table]))
    doc.build(elements, onFirstPage=add_background, onLaterPages=add_background)
    return response


# Create your views here.
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


def movie_list(request):
    tags = Tag.objects.all()
    selected_tag_name = request.GET.get("tag")
    if selected_tag_name:
        movies = Movie.objects.filter(tags__name=selected_tag_name).distinct()
    else:
        movies = Movie.objects.all()
    
    now = timezone.now().date()

    return render(request, 'movie_list.html', {
        'movies': movies,
        'now': now,
        'tags' : tags,
        'selected_tag_name': selected_tag_name
    })

from collections import defaultdict
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from .models import Movie, Showtime

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    showtimes_by_date = defaultdict(list)
    
    # Grouping showtimes by date
    for showtime in movie.showtimes.filter(showtime__gt=timezone.now()).order_by('showtime'):
        showtime_date = showtime.showtime.date()
        showtimes_by_date[showtime_date].append(showtime)
    
    return render(request, 'movie_detail.html', {'movie': movie, 'showtimes_by_date': dict(showtimes_by_date)})


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




def selectTickets(request, cinema_hall_id, movie_id, showtime_id):
    cinema_hall = get_object_or_404(CinemaHall, id=cinema_hall_id)
    movie = get_object_or_404(Movie, id=movie_id)
    show = get_object_or_404(Showtime, id=showtime_id)
    
    print("Cinema Hall ID:", cinema_hall_id)
    print("Movie ID:", movie_id)
    print("Showtime ID:", show)

    is_wednesday = datetime.now().date().weekday() == 2

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
    return render(request, 'booking_success.html')

def generate_purchase_history(request, booking_id):
    # Get the booking instance
    booking = get_object_or_404(Booking, id=booking_id)

    # Fetch the related showtime
    showtime_instance = Showtime.objects.filter(movie=booking.movie, cinema_hall=booking.cinema_hall).first()
    showtime = showtime_instance.showtime.strftime("%Y-%m-%d %H:%M:%S") if showtime_instance else "N/A"

    # Render HTML template with context
    html = render_to_string('generating_pdf.html', {'booking': booking, 'showtime': showtime})

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
        can_edit = not booking.edited and current_time <= booking.showtime.showtime - timedelta(hours=2)
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

    if booking.edited or timezone.now() > booking.showtime.showtime - timedelta(hours=2):
        return redirect('your_bookings')

    movies = Movie.objects.all()

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
                'num_seats': booking.num_seats
            })
        return redirect('confirm_edit_booking', booking_id=booking_id, showtime_id=showtime_id, seats=','.join(selected_seat_ids))

    return render(request, 'edit_seats.html', {
        'showtime': showtime,
        'seats': seats,
        'num_seats': booking.num_seats
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





# Create your views here.

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

        user = User.objects.create_user(first_name=user_fname, last_name=user_lname,username=user_username, email= user_email,password=user_pwd)
        user.save()

        if not context['has_error']:

            send_activation_email(user, request)

            styled_message = mark_safe('<span style="color: black; font-weight:bold">VERIFY</span><br>We sent you an email to verify your account')
            messages.success(request, styled_message)
            return redirect('Login')

            
    return render(request, 'SignUp.html')

@auth_user_should_not_access
def Login(request):
    if request.method == 'POST':
        context = {'has_error': False, 'data': request.POST}
        username = request.POST.get('uname')
        password = request.POST.get('pwd')
        
        # Print the username and password for debugging purposes
        print(f'Username: {username}')
        print(f'Password: {password}')
        
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
            messages.error(request, 'Email is not verified, please check your email inbox')
            context['has_error'] = True
            return render(request, 'Login.html', context)
        
        # Send OTP and redirect to enter_otp view if user is authenticated and email is verified
        send_otp(request, user)
        messages.success(request, 'OTP has been sent to your registered email')
        return redirect('enter_otp')

    return render(request, 'Login.html')

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
        return redirect(reverse('Login'))
    messages.error(request, 'Your activation link is not valid.')
    return render(request,'Login.html')

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
    qr.add_data(f'otpauth://totp/{account_name}?{qr_data}')
    qr.make(fit=True)
    
    # Create a BytesIO object to hold the image data
    img_buffer = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(img_buffer, format='PNG')
    
    # Encode the image data as a base64 string
    img_str = base64.b64encode(img_buffer.getvalue()).decode()

    # Pass the base64-encoded image string to the template
    return render(request, 'security.html', {'qr_img': img_str})



