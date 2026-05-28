from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('manual/', views.ManualView.as_view(), name='manual'),
    path('favourites/toggle/', views.FavouriteToggleView.as_view(), name='favourite_toggle'),
]