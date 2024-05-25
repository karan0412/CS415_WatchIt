from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from .import views
from .views import admin_dashboard


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

    
    path('transaction_report/', views.transaction_report, name='transaction_report'),
    path('transaction-report/pdf/', views.transaction_report_pdf, name='transaction_report_pdf'),
    path('edit_booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('edit_showtime/<int:booking_id>/<int:movie_id>/<int:cinema_hall_id>/', views.edit_showtime, name='edit_showtime'),
    path('edit_seats/<int:booking_id>/<int:showtime_id>/<int:cinema_hall_id>/', views.edit_seats, name='edit_seats'),
    path('confirm_edit_booking/<int:booking_id>/<int:showtime_id>/<str:seats>/', views.confirm_edit_booking, name='confirm_edit_booking'),
    path('recommendations/', views.movie_recommendations, name='movie_recommendations'),
    path('activate-user/<uidb64>/<token>', views.activate_user, name='activate'),
    path('Login/forget_password/', views.forget_password, name='forget_password'),
    path('reset_password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('enter_otp/', views.enter_otp, name='enter_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('QRcode', views.QRcode, name='QRcode'),
    # path('admin_tools/', include('admin_tools.urls')),
    # path('admin/user_chart/', views.generate_user_chart, name='user_chart_view'),
    path('user_activity_report/', views.user_activity_report_view, name='user_activity_report'),
    path('sales_report/', views.sales_report_view, name='sales_report'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_dashboard/minute_sales/', views.minute_sales, name='admin_dashboard_minute_sales'),
    path('admin_dashboard/minute_registrations/', views.minute_registrations, name='admin_dashboard_minute_registrations'),
    path('submit_feedback/',views.submit_feedback, name='submit_feedback'),
    # path('career_application/', views.career_application, name='career_application'),
    # path('career_applications_list/', views.career_applications_list, name='career_applications_list'),
    # path('approve_application/<int:application_id>/', views.approve_application, name='approve_application'),
    # path('reject_application/<int:application_id>/', views.reject_application, name='reject_application'),
    path('feedback_list/', views.feedback_list, name='feedback_list'),
    path('approve_feedback/<int:feedback_id>/', views.approve_feedback, name='approve_feedback'),
    path('reject_feedback/<int:feedback_id>/', views.reject_feedback, name='reject_feedback'),
    path('my_feedback/', views.my_feedback, name='my_feedback'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    