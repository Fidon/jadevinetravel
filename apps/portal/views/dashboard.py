import json
from datetime import date, timedelta

from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.utils import timezone

from apps.portal.mixins import (
    PortalRequiredMixin,
    get_accessible_bookings,
    is_mini_admin,
)
from apps.hotels.models import Hotel
from apps.cars.models import CarRental
from apps.bookings.models import Booking
from apps.contact.models import ContactMessage


class PortalDashboardView(PortalRequiredMixin, View):
    template_name = 'portal/portal_dashboard.html'

    def get(self, request):
        user = request.user
        mini_admin = is_mini_admin(user)
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        # ------------------------------------------------------------------
        # Pending approvals — Super Admin only
        # Mini-admin sees their own listings' statuses, not the global queue
        # ------------------------------------------------------------------
        pending_hotels = 0
        pending_cars = 0
        if not mini_admin:
            pending_hotels = Hotel.objects.filter(
                approval_status='pending'
            ).count()
            pending_cars = CarRental.objects.filter(
                approval_status='pending'
            ).count()

        # ------------------------------------------------------------------
        # Booking stats — scoped by role via get_accessible_bookings()
        # ------------------------------------------------------------------
        bookings_qs = get_accessible_bookings(user).select_related(
            'hotel', 'tour_package', 'car', 'user'
        )

        confirmed_paid = bookings_qs.filter(
            status='confirmed',
            payment_status='paid',
        )

        stats = {
            'today': confirmed_paid.filter(
                created_at__date=today
            ).count(),
            'this_week': confirmed_paid.filter(
                created_at__date__gte=week_start
            ).count(),
            'this_month': confirmed_paid.filter(
                created_at__date__gte=month_start
            ).count(),
        }

        # Revenue — USD only for simplicity; TZS bookings excluded here
        revenue = confirmed_paid.filter(
            currency='USD'
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0

        # Booking status breakdown
        status_counts = bookings_qs.values('status').annotate(
            count=Count('id')
        )
        status_map = {row['status']: row['count'] for row in status_counts}

        # ------------------------------------------------------------------
        # Recent bookings — last 10
        # ------------------------------------------------------------------
        recent_bookings = bookings_qs.order_by('-created_at')[:10]
        
        # Resolve tour names with language fallback before passing to template
        # so the template doesn't need to call methods with args
        lang = request.LANGUAGE_CODE
        for b in recent_bookings:
            if b.service_type == 'tour' and b.tour_package:
                b.ttour_name_display = (
                    getattr(b.tour_package, f'name_{lang}', None)
                    or b.tour_package.name_en
                )

        # ------------------------------------------------------------------
        # Unread contact messages — Super Admin only
        # ------------------------------------------------------------------
        unread_messages = 0
        if not mini_admin:
            unread_messages = ContactMessage.objects.filter(
                status='new'
            ).count()

        # ------------------------------------------------------------------
        # Mini-admin: own listing statuses
        # ------------------------------------------------------------------
        mini_admin_hotels = None
        mini_admin_cars = None
        if mini_admin:
            mini_admin_hotels = Hotel.objects.filter(
                created_by=user
            ).values('approval_status').annotate(count=Count('id'))
            mini_admin_cars = CarRental.objects.filter(
                created_by=user
            ).values('approval_status').annotate(count=Count('id'))

        context = {
            'pending_hotels': pending_hotels,
            'pending_cars': pending_cars,
            'pending_total': pending_hotels + pending_cars,
            'stats': stats,
            'revenue_usd': revenue,
            'status_map': status_map,
            'recent_bookings': recent_bookings,
            'unread_messages': unread_messages,
            'mini_admin': mini_admin,
            'mini_admin_hotels': mini_admin_hotels,
            'mini_admin_cars': mini_admin_cars,
        }
        return render(request, self.template_name, context)


class PendingCountAPIView(PortalRequiredMixin, View):
    """
    Lightweight JSON endpoint polled every 60 seconds by portal_base.js.
    One DB query. No template rendering. Returns counts for sidebar badge
    and dashboard cards.
    Super Admin: real pending counts.
    Mini-Admin: always returns zeros (they don't manage the approval queue).
    """

    def get(self, request):
        if is_mini_admin(request.user):
            return JsonResponse({'hotels': 0, 'cars': 0, 'total': 0})

        hotels = Hotel.objects.filter(approval_status='pending').count()
        cars = CarRental.objects.filter(approval_status='pending').count()

        return JsonResponse({
            'hotels': hotels,
            'cars': cars,
            'total': hotels + cars,
        })