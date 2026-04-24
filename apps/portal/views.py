from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class PortalDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'portal/portal_dashboard.html'
    login_url = '/portal/login/'

class PortalLoginView(TemplateView):
    template_name = 'portal/portal_login.html'