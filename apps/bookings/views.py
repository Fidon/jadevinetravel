from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import HttpResponseBadRequest

from .models import Booking
from .forms import HotelBookingForm, CarBookingForm, PaymentModeForm, TourBookingForm
from apps.hotels.models import Hotel, HotelRoomType
from apps.cars.models import CarRental
from apps.tours.models import TourPackage


# ---------------------------------------------------------------------------
# Session key constant
# ---------------------------------------------------------------------------
SESSION_BOOKING_KEY = 'pending_booking'


# ---------------------------------------------------------------------------
# Hotel Booking
# ---------------------------------------------------------------------------
class HotelBookingView(View):
    """
    POST only. Receives booking form from hotel detail page.
    Stores validated data + snapshotted price in session. No DB write.
    """

    def post(self, request, slug, *args, **kwargs):
        hotel = get_object_or_404(
            Hotel, slug=slug, is_active=True, approval_status='approved'
        )
        form = HotelBookingForm(request.POST)

        if not form.is_valid():
            request.session['booking_form_errors'] = form.errors.as_json()
            request.session['booking_prefill'] = request.POST.dict()
            return redirect('hotels:detail', slug=slug)

        room_type_id = form.cleaned_data['room_type_id']
        try:
            room_type = hotel.room_types.get(id=room_type_id, is_available=True)
        except HotelRoomType.DoesNotExist:
            messages.error(request, _('Selected room type is not available.'))
            return redirect('hotels:detail', slug=slug)

        num_guests = form.cleaned_data['num_guests']
        if num_guests > room_type.max_guests:
            messages.error(
                request,
                _('This room type accommodates a maximum of %(max)s guests.')
                % {'max': room_type.max_guests}
            )
            request.session['booking_prefill'] = request.POST.dict()
            return redirect('hotels:detail', slug=slug)

        check_in = form.cleaned_data['check_in_date']
        check_out = form.cleaned_data['check_out_date']
        nights = (check_out - check_in).days
        price_per_night = room_type.get_display_price()
        total_price = price_per_night * nights

        request.session[SESSION_BOOKING_KEY] = {
            'service_type': 'hotel',
            'hotel_id': hotel.id,
            'hotel_name': hotel.name,
            'hotel_slug': hotel.slug,
            'room_type_id': room_type.id,
            'room_type_name': room_type.name,
            'check_in_date': str(check_in),
            'check_out_date': str(check_out),
            'nights': nights,
            'num_guests': num_guests,
            'special_requests': form.cleaned_data.get('special_requests', ''),
            'price_per_night': str(price_per_night),
            'total_price': str(total_price),
            'currency': 'USD',
            'created_at': str(timezone.now()),
            'allows_pay_on_arrival': room_type.allows_pay_on_arrival,
            'is_refundable': room_type.is_refundable,
        }

        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/book/summary/pending/')

        return redirect('bookings:summary', reference='pending')


# ---------------------------------------------------------------------------
# Car Booking
# ---------------------------------------------------------------------------
class CarBookingView(View):

    def post(self, request, slug, *args, **kwargs):
        car = get_object_or_404(
            CarRental, slug=slug,
            is_active=True, is_available=True, approval_status='approved'
        )
        form = CarBookingForm(request.POST)

        if not form.is_valid():
            request.session['booking_form_errors'] = form.errors.as_json()
            request.session['booking_prefill'] = request.POST.dict()
            return redirect('cars:detail', slug=slug)

        rental_mode = form.cleaned_data['rental_mode']

        if rental_mode == 'self_drive' and not car.offers_self_drive:
            messages.error(request, _('This vehicle does not offer self-drive rental.'))
            return redirect('cars:detail', slug=slug)
        if rental_mode == 'with_driver' and not car.offers_driver:
            messages.error(request, _('This vehicle does not offer a driver option.'))
            return redirect('cars:detail', slug=slug)

        pickup = form.cleaned_data['pickup_date']
        returns = form.cleaned_data['return_date']
        num_days = (returns - pickup).days
        total_price = car.get_display_price() * num_days

        request.session[SESSION_BOOKING_KEY] = {
            'service_type': 'car',
            'car_id': car.id,
            'car_name': str(car),
            'car_slug': car.slug,
            'vehicle_type': car.get_vehicle_type_display(),
            'rental_mode': rental_mode,
            'pickup_location': form.cleaned_data['pickup_location'],
            'pickup_date': str(pickup),
            'return_date': str(returns),
            'num_days': num_days,
            'driver_licence_number': form.cleaned_data.get('driver_licence_number', ''),
            'special_requests': form.cleaned_data.get('special_requests', ''),
            'price_per_day': str(car.get_display_price()),
            'total_price': str(total_price),
            'currency': 'USD',
            'created_at': str(timezone.now()),
            'allows_pay_on_arrival': car.allows_pay_on_arrival,
            'is_refundable': car.is_refundable,
        }

        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/book/summary/pending/')

        return redirect('bookings:summary', reference='pending')


# ---------------------------------------------------------------------------
# Tour Booking
# ---------------------------------------------------------------------------
class TourBookingView(View):
    """
    POST only. Receives booking form from tour detail page.
    Tours are ALWAYS status='pending_confirmation' — Jadevine confirms date manually.
    Same session-first pattern as Hotel and Car.
    """

    def post(self, request, slug, *args, **kwargs):
        tour = get_object_or_404(TourPackage, slug=slug, is_active=True)
        form = TourBookingForm(request.POST)

        if not form.is_valid():
            request.session['booking_form_errors'] = form.errors.as_json()
            request.session['booking_prefill'] = request.POST.dict()
            return redirect('tours:detail', slug=slug)

        num_participants = form.cleaned_data['num_participants']

        # Cross-object validation: participant count vs. tour capacity
        if num_participants > tour.group_size_max:
            messages.error(
                request,
                _('This tour accommodates a maximum of %(max)s participants.')
                % {'max': tour.group_size_max}
            )
            request.session['booking_prefill'] = request.POST.dict()
            return redirect('tours:detail', slug=slug)

        preferred_date = form.cleaned_data['preferred_date']
        total_price = tour.get_display_price() * num_participants

        request.session[SESSION_BOOKING_KEY] = {
            'service_type': 'tour',
            'tour_id': tour.id,
            'tour_name': tour.get_name(request.LANGUAGE_CODE),
            'tour_slug': tour.slug,
            'tour_type': tour.tour_type,
            'tour_type_display': tour.get_tour_type_display(),
            'duration_days': tour.duration_days,
            'preferred_date': str(preferred_date),
            'num_participants': num_participants,
            'special_requests': form.cleaned_data.get('special_requests', ''),
            'price_per_person': str(tour.get_display_price()),
            'total_price': str(total_price),
            'currency': 'USD',
            'created_at': str(timezone.now()),
            'allows_pay_on_arrival': tour.allows_pay_on_arrival,
            'is_refundable': tour.is_refundable,
        }

        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/book/summary/pending/')

        return redirect('bookings:summary', reference='pending')


# ---------------------------------------------------------------------------
# Booking Summary
# ---------------------------------------------------------------------------
class BookingSummaryView(LoginRequiredMixin, View):
    template_name = 'bookings/booking_summary.html'
    login_url = '/accounts/login/'

    def _get_session_data(self, request):
        return request.session.get(SESSION_BOOKING_KEY)

    def get(self, request, reference, *args, **kwargs):
        if reference == 'pending':
            booking_data = self._get_session_data(request)
            if not booking_data:
                messages.error(request, _('Your booking session has expired. Please start again.'))
                return redirect('core:home')
            return render(request, self.template_name, {
                'booking_data': booking_data,
                'payment_form': PaymentModeForm(),
                'is_session_booking': True,
            })
        else:
            booking = get_object_or_404(Booking, reference=reference, user=request.user)
            return render(request, self.template_name, {
                'booking': booking,
                'is_session_booking': False,
            })

    def post(self, request, reference, *args, **kwargs):
        from django_q.tasks import async_task

        booking_data = self._get_session_data(request)
        if not booking_data:
            messages.error(request, _('Your booking session has expired. Please start again.'))
            return redirect('core:home')

        payment_form = PaymentModeForm(request.POST)
        if not payment_form.is_valid():
            return render(request, self.template_name, {
                'booking_data': booking_data,
                'payment_form': payment_form,
                'is_session_booking': True,
            })

        payment_mode = payment_form.cleaned_data['payment_mode']
        booking = self._create_booking(request, booking_data, payment_mode)

        if SESSION_BOOKING_KEY in request.session:
            del request.session[SESSION_BOOKING_KEY]

        if payment_mode == 'pay_on_arrival':
            booking.status = 'confirmed'
            booking.save(update_fields=['status'])
            # Queue both emails — async so they never block the redirect
            async_task(
                'apps.bookings.tasks.send_poa_booking_confirmation_customer',
                booking.id,
            )
            async_task(
                'apps.bookings.tasks.send_poa_booking_notification_admin',
                booking.id,
            )
            return redirect('bookings:confirmation', reference=booking.reference)

        # Pay Now — PesaPal and confirmation email handled in Phase 6
        return redirect('bookings:payment', reference=booking.reference)

    def _create_booking(self, request, data, payment_mode):
        from decimal import Decimal
        from datetime import date

        service_type = data['service_type']

        kwargs = {
            'user': request.user,
            'service_type': service_type,
            'total_price': Decimal(data['total_price']),
            'currency': data['currency'],
            'payment_status': 'pending',
            'special_requests': data.get('special_requests', ''),
            'status': 'pending_confirmation',
        }

        if service_type == 'hotel':
            hotel = get_object_or_404(Hotel, id=data['hotel_id'])
            room_type = get_object_or_404(HotelRoomType, id=data['room_type_id'])

            # Enforce Pay on Arrival restriction server-side
            if payment_mode == 'pay_on_arrival' and not room_type.allows_pay_on_arrival:
                payment_mode = 'pay_now'

            kwargs.update({
                'hotel': hotel,
                'room_type': room_type,
                'check_in_date': date.fromisoformat(data['check_in_date']),
                'check_out_date': date.fromisoformat(data['check_out_date']),
                'num_guests': data['num_guests'],
                'base_price': Decimal(data['price_per_night']),
                'is_refundable': room_type.is_refundable,
            })

        elif service_type == 'car':
            car = get_object_or_404(CarRental, id=data['car_id'])

            if payment_mode == 'pay_on_arrival' and not car.allows_pay_on_arrival:
                payment_mode = 'pay_now'

            kwargs.update({
                'car': car,
                'rental_mode': data['rental_mode'],
                'pickup_location': data['pickup_location'],
                'pickup_date': date.fromisoformat(data['pickup_date']),
                'return_date': date.fromisoformat(data['return_date']),
                'num_days': data['num_days'],
                'driver_licence_number': data.get('driver_licence_number', ''),
                'base_price': Decimal(data['price_per_day']),
                'is_refundable': car.is_refundable,
            })

        elif service_type == 'tour':
            tour = get_object_or_404(TourPackage, id=data['tour_id'])

            if payment_mode == 'pay_on_arrival' and not tour.allows_pay_on_arrival:
                payment_mode = 'pay_now'

            kwargs.update({
                'tour_package': tour,
                'preferred_date': date.fromisoformat(data['preferred_date']),
                'num_participants': data['num_participants'],
                'base_price': Decimal(data['price_per_person']),
                'is_refundable': tour.is_refundable,
            })

        kwargs['payment_mode'] = payment_mode
        return Booking.objects.create(**kwargs)


# ---------------------------------------------------------------------------
# Payment Options — stub, Phase 6 wires PesaPal
# ---------------------------------------------------------------------------
class PaymentOptionsView(LoginRequiredMixin, View):
    template_name = 'bookings/payment_options.html'
    login_url = '/accounts/login/'

    def get(self, request, reference, *args, **kwargs):
        booking = get_object_or_404(Booking, reference=reference, user=request.user)
        return render(request, self.template_name, {
            'booking': booking,
            'pesapal_stub': True,
        })


# ---------------------------------------------------------------------------
# Booking Confirmation
# ---------------------------------------------------------------------------
class BookingConfirmationView(LoginRequiredMixin, View):
    template_name = 'bookings/booking_confirmation.html'
    login_url = '/accounts/login/'

    def get(self, request, reference, *args, **kwargs):
        booking = get_object_or_404(Booking, reference=reference, user=request.user)
        return render(request, self.template_name, {'booking': booking})


# ---------------------------------------------------------------------------
# PesaPal IPN callback — stub for Phase 6
# ---------------------------------------------------------------------------
def pesapal_callback(request):
    from django.http import HttpResponse
    return HttpResponse("OK", status=200)