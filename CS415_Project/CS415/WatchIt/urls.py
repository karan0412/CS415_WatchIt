from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .import views

urlpatterns = [
    path("", views.Home, name="Home"),
    path("SignUp/", views.SignUp, name="SignUp"),
    path("Login/", views.Login, name="Login"),
    path('Loggedin/', views.Loggedin, name='Loggedin'),
    path("LogoutUser/", views.LogoutUser, name="LogoutUser"),
    path('cinema/<int:cinema_hall_id>/<int:movie_id>/<int:showtime_id>/', views.display_hall, name='display_hall'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    #path('book_seats/', views.book_seats, name='book_seats'),
    path('selectTickets/<int:cinema_hall_id>/<int:movie_id>/<int:showtime_id>/', views.selectTickets, name='selectTickets'),
    path('payment/<int:cinema_hall_id>/', views.payment, name='payment'),
    path('process-payment/', views.process_payment, name='process-payment'),
    path('booking-success/', views.booking_success, name='booking-success'),
    path('redirect_to_payment/<int:cinema_hall_id>/', views.redirect_to_payment, name='redirect_to_payment'),
    path('save_total_price_to_session/', views.save_total_price_to_session, name='save_total_price_to_session'),
    path('purchase-history/<int:booking_id>/pdf/', views.generate_purchase_history, name='generate_purchase_history'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('purchase_history/', views.list_purchase_history, name='purchase_history'),
    path('your_bookings/', views.your_bookings, name='your_bookings'),

    path('edit_booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('edit_showtime/<int:booking_id>/<int:movie_id>/<int:cinema_hall_id>/', views.edit_showtime, name='edit_showtime'),
    path('edit_seats/<int:booking_id>/<int:showtime_id>/<int:cinema_hall_id>/', views.edit_seats, name='edit_seats'),
    path('confirm_edit_booking/<int:booking_id>/<int:showtime_id>/<str:seats>/', views.confirm_edit_booking, name='confirm_edit_booking'),
    path('recommendations/', views.movie_recommendations, name='movie_recommendations'),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    