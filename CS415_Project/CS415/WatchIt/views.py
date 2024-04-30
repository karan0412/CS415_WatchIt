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
        username= request.POST.get('uname')
        password = request.POST.get('pwd')
        print({username})
        print({password})
        user = authenticate(request, username=username, password=password)
        print({user})
      
            #user = User.objects.filter(user_email=user_email)
            
            #if user_pwd == user_pwd:    
        if user is not None:     
            login(request, user)    
            return redirect('Loggedin')  # Redirect to dashboard view
        else:
            context = {'error': "Username or password did not match."}
            return render(request, 'Login.html', context)
    

    return render(request, 'Login.html')

@login_required
def Loggedin(request):
    
    return render(request, 'LoggedIn.html')


def LogoutUser(request):
    logout(request)

    return redirect('Login')


def display_hall(request, cinema_hall_id):
    cinema_hall = CinemaHall.objects.get(pk=cinema_hall_id)
    seats = list(cinema_hall.seats.all())

    # Custom alphanumeric sorting
    def alphanum_key(seat):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', seat.seat_label)]
    seats.sort(key=alphanum_key)

    # Retrieve ticket counts from session
    adult_tickets = request.session.get('adult_tickets', 0)
    child_tickets = request.session.get('child_tickets', 0)
    total_tickets = adult_tickets + child_tickets

    print("Adult Tickets: ", adult_tickets)
    print("Child Tickets: ", child_tickets)
    print("Total Tickets: ", total_tickets)


    return render(request, 'cinema.html', {
        'cinema_hall': cinema_hall,
        'seats': seats,
        'total_tickets': total_tickets,
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

def selectTickets(request, cinema_hall_id):

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
            return render(request, 'selectTickets.html', {'message': message, 'cinema_hall_id': cinema_hall_id})
        else:
            # Redirect to the display_hall view with the provided cinema hall ID and ticket counts
            request.session['adult_tickets'] = adult_tickets
            request.session['child_tickets'] = child_tickets
            request.session['total_price'] = str(total_amount)
            return redirect('display_hall', cinema_hall_id=cinema_hall_id)

    return render(request, 'selectTickets.html', {'cinema_hall_id': cinema_hall_id})

    

def successful (request):
    return redirect('succesfull')

def payment(request, cinema_hall_id):
    # Try to get the total price from the session, default to '0' if not found
    total_amount = request.session.get('total_price', '0')
    print('amount', total_amount)
    range_month = range(1, 13)
    current_year = timezone.now().year
    range_year = range(current_year, current_year + 10)

    if request.method == 'GET':
        # Retrieve selected seat IDs from the form data
        selected_seat_ids = request.GET.get('seats', '')
        seat_ids = selected_seat_ids.split(',') if selected_seat_ids else []
        seats = Seat.objects.filter(id__in=seat_ids)

        # Handle payment processing
        try:
            with transaction.atomic():
                # Create the Booking record
                booking = Booking.objects.create(
                    cinema_hall=CinemaHall.objects.get(id=cinema_hall_id),
                    payment_amount=total_amount
                )
                
                # Assign selected seats to the Booking
                booking.seats.set(seats)

                # Update seat availability
                seats.update(availability=False)

                # Clear session data related to the booking process
                request.session.pop('selected_seats', None)
                request.session.pop('total_price', None)

                # Display a success message to the user

            # Redirect to the home page
            return redirect('Home')

        except Exception as e:
            # Log the error
            # logger.error(f"Payment processing failed: {e}")
            # Display an error message to the user
            messages.error(request, 'There was an error processing your payment. Please try again.')

    # For GET request, render the payment form with the context data
    return render(request, 'payment.html', {
        'range_year': list(range_year),
        'range_month': list(range_month),
        'cinema_hall_id': cinema_hall_id,
        'total_amount': total_amount,
    })


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