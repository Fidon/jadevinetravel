from django.db import models
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class PortalRequiredMixin(AccessMixin):
    """
    Requires: authenticated + is_staff=True.
    Redirects to /portal/login/ on failure.
    Applied to EVERY portal view — no exceptions.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('portal:login')
        return super().dispatch(request, *args, **kwargs)


class SuperAdminRequiredMixin(PortalRequiredMixin):
    """
    Extends PortalRequiredMixin.
    Additionally blocks mini-admins (users with a MiniAdminProfile).
    Returns 403 — not a redirect — so the mini-admin knows exactly why they're blocked.
    """

    def dispatch(self, request, *args, **kwargs):
        result = super().dispatch(request, *args, **kwargs)
        # Honour redirect from parent (not authenticated / not staff)
        if hasattr(result, 'status_code') and result.status_code == 302:
            return result
        if hasattr(request.user, 'miniadminprofile'):
            return HttpResponseForbidden(
                "You do not have permission to access this page."
            )
        return result


# Access-control query helpers
def get_accessible_hotels(user):
    """
    Super Admin → all Hotel records.
    Mini-Admin  → only Hotel records where created_by=user.
    """
    from apps.hotels.models import Hotel

    if hasattr(user, 'miniadminprofile'):
        return Hotel.objects.filter(created_by=user)
    return Hotel.objects.all()


def get_accessible_cars(user):
    """
    Super Admin → all CarRental records.
    Mini-Admin  → only CarRental records where created_by=user.
    """
    from apps.cars.models import CarRental

    if hasattr(user, 'miniadminprofile'):
        return CarRental.objects.filter(created_by=user)
    return CarRental.objects.all()


def get_accessible_bookings(user):
    """
    Super Admin → all Booking records.
    Mini-Admin  → bookings for their own hotels and cars only.
    """
    from apps.bookings.models import Booking
    from apps.hotels.models import Hotel
    from apps.cars.models import CarRental

    if hasattr(user, 'miniadminprofile'):
        hotel_ids = Hotel.objects.filter(
            created_by=user
        ).values_list('id', flat=True)
        car_ids = CarRental.objects.filter(
            created_by=user
        ).values_list('id', flat=True)
        return Booking.objects.filter(
            models.Q(hotel_id__in=hotel_ids) |
            models.Q(car_id__in=car_ids)
        )
    return Booking.objects.all()


def get_accessible_reviews(user):
    """
    Super Admin → all Review records across all service types.
    Mini-Admin  → reviews for their own hotel and car listings only.
    """
    from apps.reviews.models import Review
    from apps.hotels.models import Hotel
    from apps.cars.models import CarRental

    if hasattr(user, 'miniadminprofile'):
        hotel_ids = Hotel.objects.filter(
            created_by=user
        ).values_list('id', flat=True)
        car_ids = CarRental.objects.filter(
            created_by=user
        ).values_list('id', flat=True)
        return Review.objects.filter(
            models.Q(hotel_id__in=hotel_ids) |
            models.Q(car_id__in=car_ids)
        )
    return Review.objects.all()


def is_mini_admin(user):
    """Convenience boolean — this'll be used in templates via context or view logic."""
    return hasattr(user, 'miniadminprofile')