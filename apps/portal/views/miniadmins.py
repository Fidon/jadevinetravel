from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from django.views import View
from django import forms as django_forms
from django_q.tasks import async_task

from apps.accounts.models import CustomUser, MiniAdminProfile
from apps.hotels.models import Hotel
from apps.cars.models import CarRental
from apps.bookings.models import Booking
from apps.portal.mixins import SuperAdminRequiredMixin
from apps.portal.tasks import _get_portal_url


# ---------------------------------------------------------------------------
# Forms — defined here because they are only used by this view module
# ---------------------------------------------------------------------------

class MiniAdminCreateForm(django_forms.Form):
    first_name = django_forms.CharField(
        max_length=150,
        widget=django_forms.TextInput(attrs={
            'class': 'jd-input',
            'placeholder': _('First name'),
        }),
        label=_('First Name'),
    )
    last_name = django_forms.CharField(
        max_length=150,
        widget=django_forms.TextInput(attrs={
            'class': 'jd-input',
            'placeholder': _('Last name'),
        }),
        label=_('Last Name'),
    )
    username = django_forms.CharField(
        max_length=150,
        widget=django_forms.TextInput(attrs={
            'class': 'jd-input',
            'placeholder': _('e.g. goldentulip_zanzibar'),
        }),
        label=_('Username'),
        help_text=_('Used to log in to the portal.'),
    )
    username = django_forms.CharField(
        max_length=150,
        widget=django_forms.TextInput(attrs={
            'class': 'jd-input',
            'placeholder': _('e.g. golden_tulip or serena or zanzibar2'),
        }),
        label=_('Username'),
        help_text=_(
            'Must start with a letter and be at least 5 characters long. '
        ),
    )
    email = django_forms.EmailField(
        widget=django_forms.EmailInput(attrs={
            'class': 'jd-input',
            'placeholder': 'partner@example.com',
        }),
        label=_('Email Address'),
    )

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
            
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise django_forms.ValidationError(
                _('This username is already taken.')
            )

        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise django_forms.ValidationError(
                _('An account with this email already exists.')
            )
        return email


class MiniAdminEditForm(django_forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': django_forms.TextInput(attrs={'class': 'jd-input'}),
            'last_name': django_forms.TextInput(attrs={'class': 'jd-input'}),
            'email': django_forms.EmailInput(attrs={'class': 'jd-input'}),
            'phone': django_forms.TextInput(attrs={'class': 'jd-input', 'placeholder': '+255 7XX XXX XXX',}),
        }
        labels = {
            'first_name': _('First Name'),
            'last_name':  _('Last Name'),
            'email':      _('Email Address'),
            'phone':      _('Phone (optional)'),
        }

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name'].strip().capitalize()
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name'].strip().capitalize()
        return last_name

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise django_forms.ValidationError(
                _('An account with this email already exists.')
            )
        return email


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_miniadmin(pk):
    """Returns a CustomUser that has a MiniAdminProfile. 404 otherwise."""
    user = get_object_or_404(CustomUser, pk=pk, is_staff=True)
    # Confirm it's actually a mini-admin, not a super admin
    get_object_or_404(MiniAdminProfile, user=user)
    return user


def _miniadmin_stats(user):
    """Returns listing and booking counts for the mini-admin detail page."""
    hotel_ids = Hotel.objects.filter(
        created_by=user
    ).values_list('id', flat=True)
    car_ids = CarRental.objects.filter(
        created_by=user
    ).values_list('id', flat=True)

    from django.db.models import Q
    bookings = Booking.objects.filter(
        Q(hotel_id__in=hotel_ids) | Q(car_id__in=car_ids)
    )

    return {
        'hotel_count':     Hotel.objects.filter(created_by=user).count(),
        'car_count':       CarRental.objects.filter(created_by=user).count(),
        'approved_hotels': Hotel.objects.filter(
            created_by=user, approval_status='approved'
        ).count(),
        'pending_hotels':  Hotel.objects.filter(
            created_by=user, approval_status='pending'
        ).count(),
        'approved_cars':   CarRental.objects.filter(
            created_by=user, approval_status='approved'
        ).count(),
        'pending_cars':    CarRental.objects.filter(
            created_by=user, approval_status='pending'
        ).count(),
        'booking_count':   bookings.count(),
    }


# ===========================================================================
# VIEWS
# ===========================================================================

class PortalMiniAdminListView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_miniadmins_list.html'

    def get(self, request):
        mini_admins = CustomUser.objects.filter(
            is_staff=True,
            miniadminprofile__isnull=False,
        ).select_related('miniadminprofile').order_by('-miniadminprofile__created_at')

        context = {
            'mini_admins': mini_admins,
            'total_count': mini_admins.count(),
            'active_count': mini_admins.filter(is_active=True).count(),
        }
        return render(request, self.template_name, context)


class PortalMiniAdminCreateView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_miniadmin_form.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form': MiniAdminCreateForm(),
            'is_edit': False,
        })

    def post(self, request):
        form = MiniAdminCreateForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {
                'form': form,
                'is_edit': False,
            })

        data = form.cleaned_data
        user = CustomUser.objects.create_user(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'].capitalize(),
            last_name=data['last_name'].capitalize(),
            is_staff=True,
            is_active=True,
            password=None,
        )
        # create_user with password=None calls set_unusable_password internally
        # Verify this explicitly in case Django version behaviour differs
        user.set_unusable_password()
        user.save(update_fields=['password'])

        MiniAdminProfile.objects.create(
            user=user,
            created_by=request.user,
        )

        async_task(
            'apps.portal.tasks.send_miniadmin_welcome_email',
            user.pk
        )

        messages.success(
            request,
            _(f'Partner account for {user.get_full_name()} created. '
              f'A welcome email with login instructions has been sent to {user.email}.')
        )
        return redirect('portal:miniadmin_detail', pk=user.pk)


class PortalMiniAdminDetailView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_miniadmin_detail.html'

    def get(self, request, pk):
        user = _get_miniadmin(pk)
        hotels = Hotel.objects.filter(
            created_by=user
        ).prefetch_related('photos').order_by('-created_at')
        cars = CarRental.objects.filter(
            created_by=user
        ).prefetch_related('photos').order_by('-created_at')

        context = {
            'partner': user,
            'hotels': hotels,
            'cars': cars,
            **_miniadmin_stats(user),
        }
        return render(request, self.template_name, context)


class PortalMiniAdminEditView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_miniadmin_form.html'

    def get(self, request, pk):
        user = _get_miniadmin(pk)
        return render(request, self.template_name, {
            'form': MiniAdminEditForm(instance=user),
            'partner': user,
            'is_edit': True,
        })

    def post(self, request, pk):
        user = _get_miniadmin(pk)
        form = MiniAdminEditForm(request.POST, instance=user)
        if not form.is_valid():
            return render(request, self.template_name, {
                'form': form,
                'partner': user,
                'is_edit': True,
            })
        form.save()
        messages.success(
            request,
            _(f'Account details for {user.get_full_name()} updated.')
        )
        return redirect('portal:miniadmin_detail', pk=pk)


class PortalMiniAdminDeactivateView(SuperAdminRequiredMixin, View):
    """POST only. Toggles is_active. Listings remain — only login is blocked."""

    def post(self, request, pk):
        user = _get_miniadmin(pk)
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])

        action = _('activated') if user.is_active else _('deactivated')
        messages.success(
            request,
            _(f'Partner account for {user.email} has been {action}. '
              f'Their listings remain unchanged.')
        )
        return redirect('portal:miniadmin_detail', pk=pk)


class PortalMiniAdminResetPasswordView(SuperAdminRequiredMixin, View):
    """
    POST only. Generates a password reset token and sends it directly
    — same token mechanism used in the welcome email.
    Does NOT use allauth's ResetPasswordForm because mini-admins
    authenticate via Django's built-in auth, not allauth.
    """

    def post(self, request, pk):
        user = _get_miniadmin(pk)

        uid   = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_path = f'/portal/set-password/{uid}/{token}/'
        reset_url  = _get_portal_url(reset_path)

        from django.core.mail import send_mail
        from django.conf import settings

        send_mail(
            subject='Reset your Jadevine Staff Portal password',
            message=(
                f'Hello {user.first_name or user.username},\n\n'
                f'A password reset was requested for your staff portal account.\n\n'
                f'Click the link below to set a new password:\n{reset_url}\n\n'
                f'This link expires in 3 days. If you did not request this, '
                f'ignore this email.\n\n'
                f'Jadevine Travel & Tours'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        messages.success(
            request,
            _(f'Password reset email sent to {user.email}.')
        )
        return redirect('portal:miniadmin_detail', pk=pk)