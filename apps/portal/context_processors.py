from apps.hotels.models import Hotel
from apps.cars.models import CarRental
from apps.contact.models import ContactMessage
from apps.reviews.models import Review
from apps.portal.mixins import is_mini_admin, get_accessible_reviews


def portal_context(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return {
            'pending_total': 0,
            'pending_hotels': 0,
            'pending_cars': 0,
            'unread_messages': 0,
            'pending_reviews': 0,
            'mini_admin': False,
        }

    mini = is_mini_admin(request.user)

    pending_hotels = 0
    pending_cars = 0
    unread_messages = 0

    if not mini:
        pending_hotels = Hotel.objects.filter(approval_status='pending').count()
        pending_cars = CarRental.objects.filter(approval_status='pending').count()
        unread_messages = ContactMessage.objects.filter(status='new').count()

    # Both roles can moderate reviews scoped to their access
    pending_reviews = get_accessible_reviews(request.user).filter(
        status='pending'
    ).count()

    return {
        'pending_total': pending_hotels + pending_cars,
        'pending_hotels': pending_hotels,
        'pending_cars': pending_cars,
        'unread_messages': unread_messages,
        'pending_reviews': pending_reviews,
        'mini_admin': mini,
    }