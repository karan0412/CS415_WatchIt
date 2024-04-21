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
    path('cinema/<int:cinema_hall_id>/', views.display_hall, name='display_hall'),
    path('movies/', views.movie_list, name='movie_list'),
    path('book_seats/', views.book_seats, name='book_seats'),
    path('selectTickets/<int:cinema_hall_id>/', views.selectTickets, name='select_tickets'),
    path('payment/<int:cinema_hall_id>/', views.payment, name='payment'),
    path('successfull/<int:cinema_hall_id>/', views.successful, name="succesfull"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    