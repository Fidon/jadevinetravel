from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('bookings/', views.BookingHistoryView.as_view(), name='booking_history'),
    path('bookings/<str:reference>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('bookings/<str:reference>/cancel/', views.CancelBookingView.as_view(), name='cancel_booking'),
    path('bookings/<str:reference>/pdf/', views.BookingPDFView.as_view(), name='booking_pdf'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('favourites/', views.FavouritesView.as_view(), name='favourites'),
    path('favourites/toggle/', views.ToggleFavouriteView.as_view(), name='toggle_favourite'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),
]