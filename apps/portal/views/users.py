from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.accounts.models import CustomUser
from apps.bookings.models import Booking
from apps.portal.mixins import SuperAdminRequiredMixin


def _get_customer(pk):
    """
    Returns a non-staff CustomUser. Staff accounts are managed via
    the Mini-Admins section — they must never appear in customer management.
    """
    return get_object_or_404(CustomUser, pk=pk, is_staff=False)


class PortalUserListView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_users_list.html'

    def get(self, request):
        qs = CustomUser.objects.filter(
            is_staff=False
        ).annotate(
            booking_count=Count('bookings', distinct=True)
        ).order_by('-date_joined')

        search = request.GET.get('q', '').strip()
        active_filter = request.GET.get('active', '').strip()

        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)  |
                Q(email__icontains=search)
            )

        if active_filter == '1':
            qs = qs.filter(is_active=True)
        elif active_filter == '0':
            qs = qs.filter(is_active=False)

        paginator  = Paginator(qs, 25)
        page_obj   = paginator.get_page(request.GET.get('page'))

        context = {
            'page_obj': page_obj,
            'search': search,
            'active_filter': active_filter,
            'total_count': CustomUser.objects.filter(is_staff=False).count(),
            'active_count': CustomUser.objects.filter(
                is_staff=False, is_active=True
            ).count(),
        }
        return render(request, self.template_name, context)


class PortalUserDetailView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_user_detail.html'

    def get(self, request, pk):
        user = _get_customer(pk)
        bookings = Booking.objects.filter(
            user=user
        ).select_related(
            'hotel', 'tour_package', 'car'
        ).order_by('-created_at')

        context = {
            'customer': user,
            'bookings': bookings,
            'booking_count': bookings.count(),
            'confirmed_count': bookings.filter(status='confirmed').count(),
            'cancelled_count': bookings.filter(status='cancelled').count(),
            'completed_count': bookings.filter(status='completed').count(),
        }
        return render(request, self.template_name, context)


class PortalUserDeactivateView(SuperAdminRequiredMixin, View):
    """POST only. Toggles is_active. Never deletes — data retention."""

    def post(self, request, pk):
        user = _get_customer(pk)

        # Prevent deactivating a user with active confirmed bookings
        active_bookings = Booking.objects.filter(
            user=user,
            status__in=['pending_confirmation', 'confirmed']
        ).count()

        if active_bookings > 0 and user.is_active:
            messages.error(
                request,
                _(f'Cannot deactivate {user.email} — they have '
                  f'{active_bookings} active booking(s). '
                  f'Resolve those bookings first.')
            )
            return redirect('portal:user_detail', pk=pk)

        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])

        action = _('activated') if user.is_active else _('deactivated')
        messages.success(
            request,
            _(f'Account for {user.email} has been {action}.')
        )
        return redirect('portal:user_detail', pk=pk)


class PortalUserResetPasswordView(SuperAdminRequiredMixin, View):
    """
    POST only. Generates a password reset token using Django's
    default_token_generator and sends it via allauth's email flow.
    We do NOT use async_task here — the token must be generated and
    emailed atomically. If the task ran later, the session state that
    allauth needs for HMAC verification might differ.
    """

    def post(self, request, pk):
        user = _get_customer(pk)

        # Allauth sends the reset email through its own machinery.
        # We trigger it by calling the same method allauth's password
        # reset view calls internally.
        from allauth.account.forms import ResetPasswordForm
        form = ResetPasswordForm(data={'email': user.email})
        if form.is_valid():
            form.save(request)
            messages.success(
                request,
                _(f'Password reset email sent to {user.email}.')
            )
        else:
            # Email not found in allauth's lookup (e.g. unverified) —
            # fall back to Django's token generator directly.
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            from apps.portal.tasks import _get_portal_url

            uid   = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_path = f'/accounts/password/reset/key/{uid}-{token}/'
            reset_url  = _get_portal_url(reset_path)

            # Send a plain transactional email — no async_task needed
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                subject='Reset your Jadevine password',
                message=(
                    f'Hello {user.first_name or user.email},\n\n'
                    f'A password reset was requested for your account.\n\n'
                    f'Click the link below to reset your password:\n{reset_url}\n\n'
                    f'This link expires in 3 days.\n\n'
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

        return redirect('portal:user_detail', pk=pk)