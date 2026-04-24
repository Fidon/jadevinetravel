from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.ContactView.as_view(), name='contact'),
    path('newsletter/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
]