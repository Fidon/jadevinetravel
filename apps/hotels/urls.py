from django.urls import path
from . import views
from apps.bookings.views import HotelBookingView

app_name = 'hotels'

urlpatterns = [
    path('', views.HotelListView.as_view(), name='list'),
    path('<slug:slug>/', views.HotelDetailView.as_view(), name='detail'),
    path('<slug:slug>/book/', HotelBookingView.as_view(), name='book'),
]