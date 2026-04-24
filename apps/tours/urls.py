from django.urls import path
from . import views
from apps.bookings.views import TourBookingView

app_name = 'tours'

urlpatterns = [
    path('', views.TourListView.as_view(), name='list'),
    path('<slug:slug>/', views.TourDetailView.as_view(), name='detail'),
    path('<slug:slug>/book/', TourBookingView.as_view(), name='book'),
]