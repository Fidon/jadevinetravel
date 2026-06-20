from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('pesapal/callback/', views.pesapal_callback, name='pesapal_callback'),

    # Booking flow — all require login (enforced in each view)
    path('summary/<str:reference>/', views.BookingSummaryView.as_view(), name='summary'),
    path('payment/<str:reference>/', views.PaymentOptionsView.as_view(), name='payment'),
    path('confirm/<str:reference>/', views.BookingConfirmationView.as_view(), name='confirmation'),
]