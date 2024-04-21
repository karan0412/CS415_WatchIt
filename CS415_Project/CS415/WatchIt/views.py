import datetime
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Seat, Booking, CinemaHall
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
import re
from django.http import JsonResponse
from .models import Seat, Booking, CinemaHall, Payment_detail
from django.http import JsonResponse

# Create your views here.
def Home(request):
    return render(request, 'Home.html')

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
            return redirect('login')
            
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
        # Split the seat_label into list of ([A, B, C], [1, 2, 3])
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', seat.seat_label)]
    
    seats.sort(key=alphanum_key)

    return render(request, 'cinema.html', {
        'cinema_hall': cinema_hall,
        'seats': seats,
    })


def book_seats(request):
    if request.method == 'POST':
        seat_ids = request.POST.getlist('seats[]')
        seats = Seat.objects.filter(id__in=seat_ids)
        booking = Booking.objects.create(booking_label="Booking #" + str(request.user.id))
        booking.seats.set(seats)
        for seat in seats:
            seat.availability = False
            seat.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def selectTickets(request, cinema_hall_id):
    if request.method == 'POST':
        
        adult_tickets = request.POST.get('adult_quantity', 0)
        child_tickets = request.POST.get('child_quantity', 0)

        # Check if any tickets are selected
        if adult_tickets == '0' and child_tickets == '0':
            # If no tickets are selected, display a message
            message = "Please select at least one ticket before proceeding."
            return render(request, 'selectTickets.html', {'message': message, 'cinema_hall_id': cinema_hall_id})
        else:
            # Redirect to the display_hall view with the provided cinema hall ID
            return redirect('display_hall', cinema_hall_id=cinema_hall_id)

    # Render the template normally if tickets are selected or if it's a GET request
    return render(request, 'selectTickets.html', {'cinema_hall_id': cinema_hall_id})
    

def successful (request):
    return redirect('succesfull')

def payment(request, cinema_hall_id):

    range_month = range(1, 13)
    
    current_year = datetime.datetime.now().year
    range_year = range(current_year, current_year + 10)  # Years from current year to 10 years into the future

    if request.method == 'POST':

        cardholder_Name = request.POST.get('cardholder_Name')
        Total = request.POST.get('Total')

        Payment_detail.objects.create(payment_Name=cardholder_Name, payment_amount=Total)
        return redirect('successfull', cinema_hall_id=cinema_hall_id)  # Redirect to a success page

    return render(request, 'payment.html', {'range_year': range_year, 'range_month': range_month, 'cinema_hall_id': cinema_hall_id})