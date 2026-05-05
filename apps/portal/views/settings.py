from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django import forms as django_forms

from apps.accounts.models import CustomUser
from apps.portal.mixins import PortalRequiredMixin


# ---------------------------------------------------------------------------
# Forms
# ---------------------------------------------------------------------------

class PortalUsernameForm(django_forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = ['username']
        widgets = {
            'username': django_forms.TextInput(attrs={
                'class': 'jd-input',
                'autocomplete': 'off',
            }),
        }
        labels = {'username': _('Username')}

    def clean_username(self):
        import re
        from django.core.exceptions import ValidationError
        from django.utils.translation import gettext_lazy as _
        
        username = self.cleaned_data['username'].lower().strip()
            
        if not re.match(r'^[a-z][a-z0-9_]{4,}$', username):
            raise ValidationError(
                _('Username must start with a letter, contain only letters, '
                'numbers, or underscores, and be at least 5 characters long.')
            )

        if CustomUser.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise django_forms.ValidationError(
                _('This username is already taken.')
            )

        return username


class PortalPasswordChangeForm(PasswordChangeForm):
    """
    Thin wrapper around Django's built-in PasswordChangeForm.
    Applies jd-input CSS class to all three fields.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'jd-input'})


# ---------------------------------------------------------------------------
# View
# ---------------------------------------------------------------------------

class PortalSettingsView(PortalRequiredMixin, View):
    """
    Single page — two independent forms submitted to separate POST actions
    via the 'form_action' hidden field so both live on the same URL.
    """
    template_name = 'portal/portal_settings.html'

    def _context(self, request, username_form=None, password_form=None):
        return {
            'username_form': username_form or PortalUsernameForm(
                instance=request.user
            ),
            'password_form': password_form or PortalPasswordChangeForm(
                user=request.user
            ),
        }

    def get(self, request):
        return render(request, self.template_name, self._context(request))

    def post(self, request):
        action = request.POST.get('form_action', '')

        if action == 'username':
            form = PortalUsernameForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    _('Username updated successfully.')
                )
                return redirect('portal:settings')
            return render(
                request,
                self.template_name,
                self._context(request, username_form=form)
            )

        if action == 'password':
            form = PortalPasswordChangeForm(
                user=request.user,
                data=request.POST,
            )
            if form.is_valid():
                user = form.save()
                # Critical: keeps the portal session alive after password change.
                # Without this Django invalidates the session and logs the user out.
                update_session_auth_hash(request, user)
                messages.success(
                    request,
                    _('Password changed successfully.')
                )
                return redirect('portal:settings')
            return render(
                request,
                self.template_name,
                self._context(request, password_form=form)
            )

        # Unknown action — just re-render
        return render(request, self.template_name, self._context(request))