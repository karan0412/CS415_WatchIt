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
]