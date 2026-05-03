from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('submit/<str:reference>/', views.SubmitReviewView.as_view(), name='submit'),
]