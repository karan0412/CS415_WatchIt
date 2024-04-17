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
    path('book_seats/', views.book_seats, name='book_seats'),
    path("selectTickets",views.selectTickets, name = "SelectTickets"),
    path("payment/", views.payment, name="payment"),
    path("succesfull/", views.successful, name="succesfull"),


]