from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View
from django.utils.translation import gettext_lazy as _
from apps.portal.mixins import PortalRequiredMixin


class PortalLoginView(View):
    """
    Username + password login for staff users.
    Completely separate from the public /accounts/login/ allauth flow.
    A customer account (is_staff=False) cannot authenticate here even with
    correct credentials — the is_staff check is explicit in post().
    """
    template_name = 'portal/portal_login.html'

    def get(self, request):
        # Already authenticated staff → redirect to dashboard
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('portal:dashboard')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username', '').strip().lower()
        password = request.POST.get('password', '')

        if not username or not password:
            return render(request, self.template_name, {
                'error': _('Username and password are required.'),
                'username': username,
            })

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, self.template_name, {
                'error': _('Incorrect username or password.'),
                'username': username,
            })

        if not user.is_staff:
            # Valid credentials for a customer account — deny access explicitly.
            # Do NOT reveal whether the account exists or what type it is.
            return render(request, self.template_name, {
                'error': _('Incorrect username or password.'),
                'username': username,
            })

        if not user.is_active:
            return render(request, self.template_name, {
                'error': _('This account has been deactivated. Contact your administrator.'),
                'username': username,
            })

        login(request, user)

        # Honour ?next= parameter — only for portal URLs to prevent open redirect
        next_url = request.POST.get('next', '').strip()
        if next_url and next_url.startswith('/portal/'):
            return redirect(next_url)

        return redirect('portal:dashboard')


class PortalLogoutView(PortalRequiredMixin, View):
    """POST-only logout. GET requests are redirected to dashboard."""

    def get(self, request):
        return redirect('portal:dashboard')

    def post(self, request):
        logout(request)
        return redirect('portal:login')