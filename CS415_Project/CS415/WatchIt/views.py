from datetime import datetime
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
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import os
from datetime import timedelta

from .recommend import get_recommendations
#from .forms import BookingForm


# Create your views here.
def Home(request):
    today = timezone.now().date()
    movies = Movie.objects.filter(release_date__lte=today)  # Fetch movies with release_date today or in the past
    deals = Deals.objects.all()
    movies_chunks = [movies[i:i+3] for i in range(0, len(movies), 3)]
    return render(request, 'Home.html', {'movies': movies, 'movies_chunks': movies_chunks, 'deals': deals,})

def SignUp (request):
    if request.method =='POST':
        user_fname = request.POST.get('user_fname')
        user_lname = request.POST.get('user_lname')
        user_email = request.POST.get('user_email')
        user_username = request.POST.get('user_username')
        user_pwd = request.POST.get('user_pwd')

        if User.objects.filter(username=user_username).exists():
            messages.error(request, "Username already exists! Please try a different username.")
            return render(request, 'SignUp.html')

        elif User.objects.filter(email=user_email).exists():
            messages.error(request, "Email already exists! Please try a different email or login.")
            return render(request, 'SignUp.html')
        
        else:
            user = User.objects.create_user(first_name=user_fname, last_name=user_lname, email=user_email, username=user_username, password=user_pwd)
            user.save()
            # Redirect to login page after successful registration
            return redirect('Login')
            
    return render(request, 'SignUp.html')

def Login(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pwd')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('Home')  # Redirect to the home page
        else:
            context = {'error': "Username or password did not match."}
            return render(request, 'Login.html', context)

    return render(request, 'Login.html')

@login_required
def Loggedin(request):
    
    return render(request, 'LoggedIn.html')


def LogoutUser(request):
    logout(request)
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

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    return render(request, 'movie_detail.html', {'movie': movie})

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
    # Corrected parameter names and use these to fetch objects
    cinema_hall = get_object_or_404(CinemaHall, id=cinema_hall_id)
    movie = get_object_or_404(Movie, id=movie_id)
    show = get_object_or_404(Showtime, id=showtime_id)
    print("Cinema Hall ID:", cinema_hall_id)
    print("Movie ID:", movie_id)
    print("Showtime ID:", show)

    if request.method == 'POST':
        adult_tickets = int(request.POST.get('adult_quantity', 0))
        child_tickets = int(request.POST.get('child_quantity', 0))
        adult_price = 7.50  # assuming $7.50 per adult ticket
        child_price = 2.50

        total_amount = (adult_tickets * adult_price) + (child_tickets * child_price)
        total_tickets = adult_tickets + child_tickets

        # Check if any tickets are selected
        if adult_tickets == 0 and child_tickets == 0:
            # If no tickets are selected, display a message
            message = "Please select at least one ticket before proceeding."
            return render(request, 'selectTickets.html', {
                'message': message, 
                'cinema_hall': cinema_hall,  # Pass objects, not IDs
                'movie': movie,
                'show': show,
            })
        else:
            # Store ticket info in session and redirect
            request.session['adult_tickets'] = adult_tickets
            request.session['child_tickets'] = child_tickets
            request.session['total_price'] = total_amount
            request.session['total_tickets'] = total_tickets
            # Redirect should use correct URL pattern and parameter names
            return redirect('display_hall', cinema_hall_id=cinema_hall_id, movie_id=movie_id, showtime_id=showtime_id)

    # Render initial form view
    return render(request, 'selectTickets.html', {
        'cinema_hall': cinema_hall,
        'movie': movie,
        'show': show,
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
    })


@csrf_exempt
@require_POST
def process_payment(request):
    # Get data from the request
    print("POST data:", request.POST) 
    cinema_hall_id = request.POST.get('cinema_hall_id')
    movie_id = request.POST.get('movie_id')
    showtime_id = request.POST.get('showtime_id')
    selected_seat_ids = [int(id) for id in request.POST.getlist('seats[]')]
    total_price = request.POST.get('total_price')
    total_tickets = request.POST.get('total_tickets')

    print("Showtime ID:", showtime_id)
    # Simulate payment processing
    payment_successful = True  # You should integrate real payment processing logic here

    if payment_successful:
        try:
            with transaction.atomic():
                # Fetch necessary objects
                cinema_hall = CinemaHall.objects.get(id=cinema_hall_id)
                movie = Movie.objects.get(id=movie_id)
                showtime = Showtime.objects.get(id=showtime_id)
                seats = Seat.objects.filter(id__in=selected_seat_ids, availability=True)

                # Check if the requested seats are still available
                if seats.count() != len(selected_seat_ids):
                    return JsonResponse({'success': False, 'error': 'One or more seats are no longer available.'})

                # Create the booking
                booking = Booking.objects.create(
                    cinema_hall=cinema_hall,
                    movie=movie,
                    payment_amount=total_price,
                    showtime=showtime,
                    num_seats=total_tickets,
                )
                if request.user.is_authenticated:
                    booking.user = request.user
                booking.seats.set(seats)
                booking.save()

                # Update seat availability
                seats.update(availability=False)

                # Success response
                return JsonResponse({'success': True})
        except Exception as e:
            # Log the exception here
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        # Payment failed
        return JsonResponse({'success': False, 'error': 'Payment processing failed.'})


def booking_success(request):
    return render(request, 'booking_success.html')

@login_required
def generate_purchase_history(request, booking_id):
    # Get the booking instance
    booking = get_object_or_404(Booking, id=booking_id)

    # Fetch the related showtime
    showtime_instance = Showtime.objects.filter(movie=booking.movie, cinema_hall=booking.cinema_hall).first()
    showtime = showtime_instance.showtime.strftime("%Y-%m-%d %H:%M:%S") if showtime_instance else "N/A"

    # Prepare the HTTP response
    response = HttpResponse(content_type='application/pdf')
    filename = f"purchase_history_{booking.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Set up the document template
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    # Get default styles and customize
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        alignment=TA_CENTER,
        fontSize=24,
        textColor=colors.black  # Black color for the title
    )
    subtitle_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        alignment=TA_CENTER,
        fontSize=18,
        textColor=colors.black  # Black color for the subtitle
    )
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['BodyText'],
        fontSize=10,
        leading=12,
        textColor=colors.black  # Black color for the text
    )
    payment_style = ParagraphStyle(
        'Payment',
        parent=styles['BodyText'],
        fontSize=12,
        leading=14,
        textColor=colors.black,  # Black color for the payment text
        fontName='Helvetica-Bold',  # Bold font
        alignment=TA_RIGHT
    )
    movie_style = ParagraphStyle(
        'Movie',
        parent=styles['BodyText'],
        fontSize=12,
        leading=14,
        textColor=colors.black,  # Black color for the movie text
        fontName='Helvetica-Bold',  # Bold font
        alignment=TA_CENTER
    )
    small_bold_style = ParagraphStyle(
        'SmallBold',
        parent=styles['BodyText'],
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.black  # Black color for the thank you message
    )
    terms_style = ParagraphStyle(
        'Terms',
        parent=styles['BodyText'],
        fontSize=8,
        leading=10,
        textColor=colors.black  # Black color for terms text
    )

    # Base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Create a function to add a background and footer to each page
    def add_background(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.white)  # White background
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1)

        # Add footer note centered
        footer_text = 'Thank you for your purchase!'
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.black)
        canvas.drawCentredString(doc.pagesize[0] / 2.0, 0.5 * inch, footer_text)  # Centering the footer text
        canvas.restoreState()

    # Add event image at the top-left corner
    image_path = os.path.join(base_dir, 'movie_images', 'WIT.jpg')
    event_image = Image(image_path, width=doc.width * 0.3, height=doc.width * 0.3)  # Adjust as needed
    elements.append(event_image)
    elements.append(Spacer(1, 20))

    # Add solid line
    elements.append(HRFlowable(width="100%", color=colors.black, lineCap='butt'))

    # Add the Movie detail centered and in bold
    movie_detail = f'<b>Movie:</b> {booking.movie.title if booking.movie else "N/A"}'
    movie_paragraph = Paragraph(movie_detail, movie_style)
    elements.append(movie_paragraph)
    elements.append(Spacer(1, 20))

    # Add receipt details including user information
    details = [
        f'<b>User:</b> {booking.user.username if booking.user else "N/A"}',
        f'<b>Cinema Hall:</b> {booking.cinema_hall.cinema_type if booking.cinema_hall else "N/A"}',
        f'<b>Showtime:</b> {showtime}',
        f'<b>Booking Date:</b> {booking.booking_date.strftime("%Y-%m-%d %H:%M:%S") if booking.booking_date else "N/A"}',
        f'<b>Seats:</b> {", ".join(seat.seat_label for seat in booking.seats.all()) or "No seats"}'
    ]

    for detail in details:
        p = Paragraph(detail, normal_style)
        elements.append(p)
        elements.append(Spacer(1, 12))

    # Add dotted line between seats and payment amount
    elements.append(HRFlowable(width="100%", color=colors.black, dash=(1, 2)))

    # Add payment amount in bold
    payment_amount_text = f'Payment Amount: ${"{:,.2f}".format(booking.payment_amount) if booking.payment_amount else "N/A"}'
    payment_amount = Paragraph(payment_amount_text, payment_style)
    elements.append(payment_amount)
    elements.append(Spacer(1, 20))

    # Add solid line
    elements.append(HRFlowable(width="100%", color=colors.black, lineCap='butt'))

    # Add terms and conditions with only bottom dotted border
    terms_text = """
    <b>Terms and Conditions for Cinema Payment</b><br/>
    <b>Acceptance of Terms</b><br/>
    By purchasing a ticket, you agree to be bound by these terms and conditions.<br/><br/>
    <b>Ticket Purchase</b><br/>
    All ticket sales are final. Once purchased, tickets cannot be transferred or refunded.<br/>
    Customers are responsible for checking the details of their booking (film, time, and date) before confirming the purchase.<br/><br/>
    <b>Payment Methods</b><br/>
    We accept major credit and debit cards, online payment platforms, and cash at the box office.<br/>
    Payment must be made in full at the time of booking.<br/><br/>
    <b>Pricing and Fees</b><br/>
    Ticket prices are subject to change without notice.<br/>
    Additional fees may apply for online bookings, premium seats, or special screenings.<br/><br/>
    <b>Discounts and Offers</b><br/>
    Discounts, vouchers, and promotional offers are subject to specific terms and conditions and may not be combined unless stated otherwise.<br/>
    Proof of eligibility may be required for discounted tickets (e.g., student ID, senior citizen card).
    """
    terms = Paragraph(terms_text, terms_style)
    elements.append(terms)
    elements.append(HRFlowable(width="100%", color=colors.black, dash=(1, 2)))

    # Build the PDF
    doc.build(elements, onFirstPage=add_background, onLaterPages=add_background)
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


