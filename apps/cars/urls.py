from django.urls import path
from . import views
from apps.bookings.views import CarBookingView

app_name = 'cars'

urlpatterns = [
    path('', views.CarListView.as_view(), name='list'),
    path('<slug:slug>/', views.CarDetailView.as_view(), name='detail'),
    path('<slug:slug>/book/', CarBookingView.as_view(), name='book'),
]