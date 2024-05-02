from datetime import datetime
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .models import User
from django.utils import timezone
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
from reportlab.lib.enums import TA_CENTER
from django.http import HttpResponse

# Create your views here.
def Home(request):
    today = timezone.now().date()
    movies = Movie.objects.filter(release_date__lte=today)  # Fetch movies with release_date today or in the past
    deals = Deals.objects.all()
    movies_chunks = [movies[i:i+3] for i in range(0, len(movies), 3)]
    return render(request, 'Home.html', {'movies': movies, 'movies_chunks': movies_chunks, 'deals': deals, })

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


def display_hall(request, cinema_hall_id, movie_id):
    
    showtime = get_object_or_404(Showtime, cinema_hall_id=cinema_hall_id, movie_id=movie_id)

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

#def book_seats(request):
 #   if request.method == 'POST':
  #      with transaction.atomic():
   #         seat_ids = request.POST.getlist('seats[]')
    #        seats = Seat.objects.filter(id__in=seat_ids)
      #      booking = Booking.objects.create(booking_label="Booking #" + str(request.user.id))
     #       booking.seats.set(seats)
       #     seats.update(availability=False)
        #return JsonResponse({'success': True})
    #else:
     #   return HttpResponseNotAllowed(['POST'])

from django.shortcuts import get_object_or_404, render, redirect

def selectTickets(request, cinema_hall_id, movie_id):
    # Corrected parameter names and use these to fetch objects
    cinema_hall = get_object_or_404(CinemaHall, id=cinema_hall_id)
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'POST':
        adult_tickets = int(request.POST.get('adult_quantity', 0))
        child_tickets = int(request.POST.get('child_quantity', 0))
        adult_price = 7.50  # assuming $7.50 per adult ticket
        child_price = 2.50

        total_amount = (adult_tickets * adult_price) + (child_tickets * child_price)

        # Check if any tickets are selected
        if adult_tickets == 0 and child_tickets == 0:
            # If no tickets are selected, display a message
            message = "Please select at least one ticket before proceeding."
            return render(request, 'selectTickets.html', {
                'message': message, 
                'cinema_hall': cinema_hall,  # Pass objects, not IDs
                'movie': movie
            })
        else:
            # Store ticket info in session and redirect
            request.session['adult_tickets'] = adult_tickets
            request.session['child_tickets'] = child_tickets
            request.session['total_price'] = total_amount
            # Redirect should use correct URL pattern and parameter names
            return redirect('display_hall', cinema_hall_id=cinema_hall_id, movie_id=movie_id)

    # Render initial form view
    return render(request, 'selectTickets.html', {
        'cinema_hall': cinema_hall,
        'movie': movie
    })


def payment(request, cinema_hall_id):
    movie_id = request.GET.get('movie_id')
    selected_seat_ids = request.GET.get('seats', '').split(',')
    total_tickets = int(request.GET.get('total_tickets', 0))
    #total_price = int(request.GET.get('total_price', 0))
    total_price = request.session.get('total_price', 0)
    
    cinema_hall = get_object_or_404(CinemaHall, id=cinema_hall_id)
    movie = get_object_or_404(Movie, id=movie_id)
    seats = Seat.objects.filter(id__in=selected_seat_ids)


    return render(request, 'payment.html', {
        'cinema_type': cinema_hall.cinema_type,
        'movie_title': movie.title,
        'movie_id': movie_id,
        'cinema_hall_id': cinema_hall_id,
        'movie_duration': movie.duration,
        'total_price': total_price,
        'selected_seats': seats,
    })


@csrf_exempt
@require_POST
def process_payment(request):
    # Get data from the request
    print("POST data:", request.POST) 
    cinema_hall_id = request.POST.get('cinema_hall_id')
    movie_id = request.POST.get('movie_id')
    selected_seat_ids = [int(id) for id in request.POST.getlist('seats[]')]
    total_price = request.POST.get('total_price')

    # Simulate payment processing
    payment_successful = True  # You should integrate real payment processing logic here

    if payment_successful:
        try:
            with transaction.atomic():
                # Fetch necessary objects
                cinema_hall = CinemaHall.objects.get(id=cinema_hall_id)
                movie = Movie.objects.get(id=movie_id)
                seats = Seat.objects.filter(id__in=selected_seat_ids, availability=True)

                # Check if the requested seats are still available
                if seats.count() != len(selected_seat_ids):
                    return JsonResponse({'success': False, 'error': 'One or more seats are no longer available.'})

                # Create the booking
                booking = Booking.objects.create(
                    cinema_hall=cinema_hall,
                    movie=movie,
                    payment_amount=total_price
                )
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


def generate_purchase_history(request, booking_id):
    # Get the booking instance
    booking = get_object_or_404(Booking, id=booking_id)

    # Prepare the HTTP response
    response = HttpResponse(content_type='application/pdf')
    filename = f"purchase_history_{booking.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Set up the document template
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Get default styles and customize
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.alignment = TA_CENTER
    title_style.fontSize = 24
    title_style.textColor = colors.HexColor('#000080')  # Dark blue color for the title

    # Add main title
    title = Paragraph('WatchIt Cinemas', title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Add subtitle
    subtitle_style = styles['Heading2']
    subtitle_style.alignment = TA_CENTER
    subtitle_style.fontSize = 18
    subtitle_style.textColor = colors.HexColor('#666666')  # Dark gray color for the subtitle
    subtitle = Paragraph('Purchase History', subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 20))

    # Define the table data
    data = [
        [
            Paragraph('<b>Cinema Hall</b>', styles['BodyText']),
            Paragraph('<b>Booking Date</b>', styles['BodyText']),
            Paragraph('<b>Payment Amount</b>', styles['BodyText']),
            Paragraph('<b>Seats</b>', styles['BodyText'])
        ],
        [
            booking.cinema_hall.cinema_type if booking.cinema_hall else 'N/A',
            booking.booking_date.strftime('%Y-%m-%d %H:%M:%S') if booking.booking_date else 'N/A',
            '${:,.2f}'.format(booking.payment_amount) if booking.payment_amount else 'N/A',
            ', '.join(seat.seat_label for seat in booking.seats.all()) or 'No seats'
        ]
    ]

    # Create the table with styled cells
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00A550')),  # Green color for the header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
    ])
    table = Table(data, colWidths=[doc.width/4.0]*4, style=table_style)
    elements.append(table)

    # Build the PDF
    doc.build(elements)
    return response



def list_purchase_history(request):
    # Fetch all bookings
    purchase_histories = Booking.objects.all()
    return render(request, 'purchase_history.html', {'purchase_histories': purchase_histories})