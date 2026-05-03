from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.bookings.models import Booking
from .forms import ReviewForm
from .models import Review


class SubmitReviewView(LoginRequiredMixin, View):
    """
    POST-only. Receives review form from booking_detail.html.
    Guards:
      - booking must belong to request.user
      - booking.status must be 'completed'
      - no existing review on this booking (OneToOneField enforced at DB level,
        but we guard before hitting the DB to give a clean user-facing message)
    On success: redirects back to booking detail with success message.
    On failure: redirects back with error message.
    No GET — if someone hits this URL directly, redirect to dashboard.
    """
    login_url = '/accounts/login/'

    def get(self, request, reference):
        return redirect('accounts:booking_detail', reference=reference)

    def post(self, request, reference):
        booking = get_object_or_404(
            Booking,
            reference=reference,
            user=request.user,
        )

        # Guard 1: only completed bookings can be reviewed
        if booking.status != 'completed':
            messages.error(
                request,
                _('You can only review a booking after the service has been completed.')
            )
            return redirect('accounts:booking_detail', reference=reference)

        # Guard 2: one review per booking
        if hasattr(booking, 'review'):
            messages.error(
                request,
                _('You have already submitted a review for this booking.')
            )
            return redirect('accounts:booking_detail', reference=reference)

        form = ReviewForm(request.POST)
        if not form.is_valid():
            # Rating field is hidden/JS-set — invalid means JS was bypassed
            messages.error(
                request,
                _('Invalid submission. Please select a rating between 1 and 10.')
            )
            return redirect('accounts:booking_detail', reference=reference)

        review = form.save(commit=False)
        review.user = request.user
        review.booking = booking
        review.service_type = booking.service_type
        review.status = 'pending'

        # Link to the correct service FK
        if booking.service_type == 'hotel':
            review.hotel = booking.hotel
        elif booking.service_type == 'tour':
            review.tour_package = booking.tour_package
        elif booking.service_type == 'car':
            review.car = booking.car

        review.save()

        messages.success(
            request,
            _('Thank you for your review! It will appear on the listing once approved.')
        )
        return redirect('accounts:booking_detail', reference=reference)