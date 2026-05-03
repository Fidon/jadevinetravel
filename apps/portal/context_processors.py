from apps.hotels.models import Hotel
from apps.cars.models import CarRental
from apps.contact.models import ContactMessage
from apps.portal.mixins import is_mini_admin


def portal_context(request):
    """
    Returns portal-wide variables available in every portal template.
    Fires only for authenticated staff users to avoid unnecessary DB queries
    on public pages that happen to use the same template engine.
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return {
            'pending_total': 0,
            'pending_hotels': 0,
            'pending_cars': 0,
            'unread_messages': 0,
            'mini_admin': False,
        }

    mini = is_mini_admin(request.user)

    pending_hotels = 0
    pending_cars = 0
    unread_messages = 0

    if not mini:
        pending_hotels = Hotel.objects.filter(
            approval_status='pending'
        ).count()
        pending_cars = CarRental.objects.filter(
            approval_status='pending'
        ).count()
        unread_messages = ContactMessage.objects.filter(
            status='new'
        ).count()

    return {
        'pending_total': pending_hotels + pending_cars,
        'pending_hotels': pending_hotels,
        'pending_cars': pending_cars,
        'unread_messages': unread_messages,
        'mini_admin': mini,
    }