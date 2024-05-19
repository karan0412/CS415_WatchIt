from datetime import datetime
import json
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
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.conf import settings
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

def Home(request):
    today = timezone.now().date()
    movies = Movie.objects.filter(release_date__lte=today)
    deals = Deals.objects.all()
    movies_chunks = [movies[i:i+3] for i in range(0, len(movies), 3)]
    return render(request, 'Home.html', {'movies': movies, 'movies_chunks': movies_chunks, 'deals': deals,})

def SignUp(request):
    if request.method == 'POST':
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
            return redirect('Login')
    return render(request, 'SignUp.html')

def Login(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pwd')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('Home')
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

    def alphanum_key(seat):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', seat.seat_label)]
    seats = sorted(seats, key=alphanum_key)

    adult_tickets = request.session.get('adult_tickets', 0)
    child_tickets = request.session.get('child_tickets', 0)
    total_tickets = adult_tickets + child_tickets

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
        'tags': tags,
        'selected_tag_name': selected_tag_name
    })

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    return render(request, 'movie_detail.html', {'movie': movie})

def redirect_to_payment(request, cinema_hall_id):
    selected_seat_ids = request.POST.getlist('seats[]')
    request.session['selected_seats'] = selected_seat_ids
    payment_url = reverse('payment', args=[cinema_hall_id]) + '?seats=' + ','.join(selected_seat_ids)
    return HttpResponseRedirect(payment_url)

@require_POST
@csrf_exempt
def save_total_price_to_session(request):
    request.session['total_price'] = request.POST.get('total_price')
    return JsonResponse({'success': True})

def selectTickets(request, cinema_hall_id, movie_id, showtime_id):
    cinema_hall = get_object_or_404(CinemaHall, id=cinema_hall_id)
    movie = get_object_or_404(Movie, id=movie_id)
    show = get_object_or_404(Showtime, id=showtime_id)

    if request.method == 'POST':
        adult_tickets = int(request.POST.get('adult_quantity', 0))
        child_tickets = int(request.POST.get('child_quantity', 0))
        adult_price = 750
        child_price = 250

        total_amount = (adult_tickets * adult_price) + (child_tickets * child_price)

        if adult_tickets == 0 and child_tickets == 0:
            messages.error(request, "Please select at least one ticket before proceeding.")
            return render(request, 'selectTickets.html', {
                'cinema_hall': cinema_hall,
                'movie': movie,
                'show': show,
            })
        else:
            try:
                logger.debug(f"Creating checkout session with total amount: {total_amount}")
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'fjd',
                            'product_data': {
                                'name': f'Tickets for {movie.title}',
                            },
                            'unit_amount': total_amount,
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri(reverse('booking_success')) + '?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=request.build_absolute_uri(reverse('selectTickets', args=[cinema_hall_id, movie_id, showtime_id])),
                )
                logger.debug(f"Checkout session created: {checkout_session.id}")
                return redirect(checkout_session.url)
            except Exception as e:
                logger.error(f"Failed to create Stripe checkout session: {e}")
                messages.error(request, "Failed to create Stripe checkout session.")
                return render(request, 'selectTickets.html', {
                    'cinema_hall': cinema_hall,
                    'movie': movie,
                    'show': show,
                    'error': str(e)
                })

    return render(request, 'selectTickets.html', {
        'cinema_hall': cinema_hall,
        'movie': movie,
        'show': show,
    })

@csrf_exempt
@require_POST
def process_payment(request):
    logger.debug(f"POST data: {request.POST}")
    session_id = request.POST.get('session_id')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        logger.debug(f"Retrieved Stripe session: {session.id}")
        cinema_hall_id = session.metadata.cinema_hall_id
        movie_id = session.metadata.movie_id
        selected_seat_ids = session.metadata.selected_seat_ids.split(',')
        total_price = session.amount_total

        with transaction.atomic():
            cinema_hall = CinemaHall.objects.get(id=cinema_hall_id)
            movie = Movie.objects.get(id=movie_id)
            seats = Seat.objects.filter(id__in=selected_seat_ids, availability=True)

            if seats.count() != len(selected_seat_ids):
                return JsonResponse({'success': False, 'error': 'One or more seats are no longer available.'})

            booking = Booking.objects.create(
                cinema_hall=cinema_hall,
                movie=movie,
                payment_amount=total_price / 100.0
            )

            if request.user.is_authenticated:
                booking.user = request.user

            booking.seats.set(seats)
            booking.save()
            seats.update(availability=False)
            return JsonResponse({'success': True})
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        logger.error(f"Error processing payment: {e}")
        return JsonResponse({'success': False, 'error': str(e)})

def payment(request, cinema_hall_id):
    movie_id = request.GET.get('movie_id')
    showtime_id = request.GET.get('showtime_id')
    selected_seat_ids = request.GET.get('seats', '').split(',')
    total_tickets = int(request.GET.get('total_tickets', 0))
    total_price = request.session.get('total_price', 0)

    cinema_hall = get_object_or_404(CinemaHall, id=cinema_hall_id)
    movie = get_object_or_404(Movie, id=movie_id)
    show = get_object_or_404(Showtime, id=showtime_id)
    seats = Seat.objects.filter(id__in=selected_seat_ids)

    return render(request, 'payment.html', {
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        'cinema_type': cinema_hall.cinema_type,
        'movie_title': movie.title,
        'movie_id': movie_id,
        'cinema_hall_id': cinema_hall_id,
        'movie_duration': movie.duration,
        'total_price': total_price,
        'selected_seats': seats,
        'show': show,
        'showtime_id': showtime_id,
    })

def booking_success(request):
    return render(request, 'booking_success.html')

@login_required
def generate_purchase_history(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    showtime_instance = Showtime.objects.filter(movie=booking.movie, cinema_hall=booking.cinema_hall).first()
    showtime = showtime_instance.showtime.strftime("%Y-%m-%d %H:%M:%S") if showtime_instance else "N/A"

    response = HttpResponse(content_type='application/pdf')
    filename = f"purchase_history_{booking.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, pagesize=A4)
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

    base_dir = os.path.dirname(os.path.abspath(__file__))

    def add_background(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.white)
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1)
        footer_text = 'Thank you for your purchase!'
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.black)
        canvas.drawCentredString(doc.pagesize[0] / 2.0, 0.5 * inch, footer_text)
        canvas.restoreState()

    image_path = os.path.join(base_dir, 'movie_images', 'WIT.jpg')
    event_image = Image(image_path, width=doc.width * 0.3, height=doc.width * 0.3)
    elements.append(event_image)
    elements.append(Spacer(1, 20))

    elements.append(HRFlowable(width="100%", color=colors.black, lineCap='butt'))

    movie_detail = f'<b>Movie:</b> {booking.movie.title if booking.movie else "N/A"}'
    movie_paragraph = Paragraph(movie_detail, movie_style)
    elements.append(movie_paragraph)
    elements.append(Spacer(1, 20))

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

    elements.append(HRFlowable(width="100%", color=colors.black, dash=(1, 2)))

    payment_amount_text = f'Payment Amount: ${"{:,.2f}".format(booking.payment_amount) if booking.payment_amount else "N/A"}'
    payment_amount = Paragraph(payment_amount_text, payment_style)
    elements.append(payment_amount)
    elements.append(Spacer(1, 20))

    elements.append(HRFlowable(width="100%", color=colors.black, lineCap='butt'))

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

    doc.build(elements, onFirstPage=add_background, onLaterPages=add_background)
    return response

@login_required
def list_purchase_history(request):
    purchase_histories = Booking.objects.filter(user=request.user)
    return render(request, 'purchase_history.html', {'purchase_histories': purchase_histories})

@csrf_exempt
def create_payment_intent(request):
    if request.method == "POST":
        data = json.loads(request.body)
        amount = int(float(data['total_price']) * 100)
        logger.debug(f"Creating payment intent for amount: {amount}")

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
            )
            logger.debug(f"Payment intent created: {intent.client_secret}")
            return JsonResponse({'clientSecret': intent.client_secret})
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Error creating Stripe payment intent: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Request method not allowed'}, status=405)
