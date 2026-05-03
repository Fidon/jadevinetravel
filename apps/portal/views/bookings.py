from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from apps.bookings.models import Booking
from apps.portal.mixins import (
    PortalRequiredMixin,
    SuperAdminRequiredMixin,
    get_accessible_bookings,
    is_mini_admin,
)
from apps.portal.forms import BookingStatusForm, STATUS_TRANSITIONS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_service_name(booking, lang='en'):
    """
    Returns the display name of the booked service.
    Resolves multilingual tour names in view — never call .get_name() from template.
    """
    if booking.service_type == 'hotel' and booking.hotel:
        return booking.hotel.name
    if booking.service_type == 'tour' and booking.tour_package:
        return (
            getattr(booking.tour_package, f'name_{lang}', None)
            or booking.tour_package.name_en
        )
    if booking.service_type == 'car' and booking.car:
        return booking.car.name
    return '—'


def _get_service_icon(service_type):
    icons = {
        'hotel': 'bi-building',
        'tour':  'bi-compass',
        'car':   'bi-car-front',
    }
    return icons.get(service_type, 'bi-calendar')


# ===========================================================================
# BOOKING LIST
# ===========================================================================

class PortalBookingListView(PortalRequiredMixin, View):
    template_name = 'portal/portal_bookings_list.html'

    def get(self, request):
        lang = request.LANGUAGE_CODE
        qs = get_accessible_bookings(request.user).select_related(
            'user', 'hotel', 'tour_package', 'car'
        )

        # Filters
        service_filter  = request.GET.get('service', '').strip()
        status_filter   = request.GET.get('status', '').strip()
        payment_filter  = request.GET.get('payment', '').strip()
        date_from       = request.GET.get('date_from', '').strip()
        date_to         = request.GET.get('date_to', '').strip()
        search_query    = request.GET.get('q', '').strip()

        if service_filter:
            qs = qs.filter(service_type=service_filter)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if payment_filter:
            qs = qs.filter(payment_status=payment_filter)
        if date_from:
            try:
                qs = qs.filter(created_at__date__gte=date_from)
            except ValueError:
                pass
        if date_to:
            try:
                qs = qs.filter(created_at__date__lte=date_to)
            except ValueError:
                pass
        if search_query:
            qs = qs.filter(
                Q(reference__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query)
            )

        # Resolve service names in view — avoids template calling methods with args
        bookings = list(qs.order_by('-created_at'))
        for b in bookings:
            b.service_name = _resolve_service_name(b, lang)
            b.service_icon = _get_service_icon(b.service_type)

        # Summary counts for filter badges
        total       = qs.count()
        pending_cnt = qs.filter(
            status__in=['pending_confirmation', 'cancellation_requested']
        ).count()

        context = {
            'bookings':       bookings,
            'total':          total,
            'pending_cnt':    pending_cnt,
            'service_filter': service_filter,
            'status_filter':  status_filter,
            'payment_filter': payment_filter,
            'date_from':      date_from,
            'date_to':        date_to,
            'search_query':   search_query,
            'mini_admin':     is_mini_admin(request.user),
            'service_choices': Booking.SERVICE_TYPE_CHOICES,
            'status_choices':  Booking.STATUS_CHOICES,
            'payment_choices': Booking.PAYMENT_STATUS_CHOICES,
        }
        return render(request, self.template_name, context)


# ===========================================================================
# BOOKING DETAIL
# ===========================================================================

class PortalBookingDetailView(PortalRequiredMixin, View):
    template_name = 'portal/portal_booking_detail.html'

    def get(self, request, pk):
        lang = request.LANGUAGE_CODE

        # Access control — get_accessible_bookings scopes by role
        accessible = get_accessible_bookings(request.user)
        booking = get_object_or_404(
            accessible.select_related(
                'user', 'hotel', 'room_type',
                'tour_package', 'car', 'cancelled_by'
            ),
            pk=pk
        )

        booking.service_name = _resolve_service_name(booking, lang)
        booking.service_icon = _get_service_icon(booking.service_type)

        # Valid status transitions for this booking
        valid_transitions = STATUS_TRANSITIONS.get(booking.status, [])
        status_form = BookingStatusForm(current_status=booking.status)

        # Can this booking be marked as paid?
        can_mark_paid = (
            booking.payment_mode == 'pay_on_arrival' and
            booking.payment_status == 'pending' and
            booking.status == 'confirmed'
        )

        context = {
            'booking':          booking,
            'status_form':      status_form,
            'valid_transitions': valid_transitions,
            'can_mark_paid':    can_mark_paid,
            'mini_admin':       is_mini_admin(request.user),
        }
        return render(request, self.template_name, context)


# ===========================================================================
# STATUS UPDATE — POST only
# ===========================================================================

class PortalBookingStatusView(PortalRequiredMixin, View):

    def post(self, request, pk):
        accessible = get_accessible_bookings(request.user)
        booking = get_object_or_404(accessible, pk=pk)

        new_status = request.POST.get('status', '').strip()
        valid_next = STATUS_TRANSITIONS.get(booking.status, [])

        if not new_status:
            messages.error(request, _('Please select a status to apply.'))
            return redirect('portal:booking_detail', pk=pk)

        if new_status not in valid_next:
            messages.error(
                request,
                _(f'Cannot transition from "{booking.get_status_display()}" '
                  f'to "{new_status}". Invalid transition.')
            )
            return redirect('portal:booking_detail', pk=pk)

        old_status = booking.status
        booking.status = new_status

        # Handle cancellation-specific fields
        if new_status == 'cancelled':
            booking.cancelled_at = timezone.now()
            booking.cancelled_by = request.user
            note = request.POST.get('admin_note', '').strip()
            if note:
                booking.cancellation_reason = note

        booking.save(update_fields=[
            'status', 'cancelled_at', 'cancelled_by', 'cancellation_reason'
        ])

        messages.success(
            request,
            _(f'Booking {booking.reference} status updated: '
              f'{old_status} → {new_status}.')
        )
        return redirect('portal:booking_detail', pk=pk)


# ===========================================================================
# MARK AS PAID — POST only (Pay on Arrival bookings)
# ===========================================================================

class PortalBookingMarkPaidView(PortalRequiredMixin, View):

    def post(self, request, pk):
        accessible = get_accessible_bookings(request.user)
        booking = get_object_or_404(accessible, pk=pk)

        if booking.payment_mode != 'pay_on_arrival':
            messages.error(
                request,
                _('Only Pay on Arrival bookings can be manually marked as paid.')
            )
            return redirect('portal:booking_detail', pk=pk)

        if booking.payment_status == 'paid':
            messages.info(request, _('This booking is already marked as paid.'))
            return redirect('portal:booking_detail', pk=pk)

        booking.payment_status = 'paid'
        booking.save(update_fields=['payment_status'])

        messages.success(
            request,
            _(f'Booking {booking.reference} marked as fully paid.')
        )
        return redirect('portal:booking_detail', pk=pk)

