from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.PortalDashboardView.as_view(), name='dashboard'),
    path('login/', views.PortalLoginView.as_view(), name='login'),
]