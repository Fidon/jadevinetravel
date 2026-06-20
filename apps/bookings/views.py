import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Booking
from .forms import HotelBookingForm, CarBookingForm, PaymentModeForm, TourBookingForm
from apps.hotels.models import Hotel, HotelRoomType
from apps.cars.models import CarRental
from apps.tours.models import TourPackage

logger = logging.getLogger(__name__)

SESSION_BOOKING_KEY = 'pending_booking'


# ---------------------------------------------------------------------------
# Hotel Booking
# ---------------------------------------------------------------------------
class HotelBookingView(View):
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

        num_adults   = form.cleaned_data['num_adults']
        num_children = form.cleaned_data['num_children']
        num_infants  = form.cleaned_data['num_infants']
        num_pets     = form.cleaned_data['num_pets']
        num_rooms    = form.cleaned_data['num_rooms']
        billable_occupants = num_adults + num_children

        max_total = room_type.max_guests * num_rooms
        if billable_occupants > max_total:
            messages.error(
                request,
                _('%(rooms)s room(s) of this type accommodate a maximum of %(max)s adults/children total.')
                % {'rooms': num_rooms, 'max': max_total}
            )
            request.session['booking_prefill'] = request.POST.dict()
            return redirect('hotels:detail', slug=slug)

        if num_pets > 0 and not room_type.allows_pets:
            messages.error(request, _('This room type does not allow pets.'))
            request.session['booking_prefill'] = request.POST.dict()
            return redirect('hotels:detail', slug=slug)

        check_in  = form.cleaned_data['check_in_date']
        check_out = form.cleaned_data['check_out_date']
        nights = (check_out - check_in).days
        original_price_per_night = room_type.get_effective_price()
        price_per_night = room_type.get_display_price()
        total_price = price_per_night * nights * num_rooms
        original_total = original_price_per_night * nights * num_rooms

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
            'num_rooms': num_rooms,
            'num_adults': num_adults,
            'num_children': num_children,
            'num_infants': num_infants,
            'num_pets': num_pets,
            'num_guests': billable_occupants,
            'special_requests': form.cleaned_data.get('special_requests', ''),
            'price_per_night': str(price_per_night),
            'original_price_per_night': str(original_price_per_night),
            'total_price': str(total_price),
            'original_total': str(original_total),
            'discount_percent': room_type.discount_percent,
            'has_discount': room_type.has_active_discount,
            'savings': str(original_total - total_price) if room_type.has_active_discount else '0',
            'currency': 'USD',
            'created_at': str(timezone.now()),
            'allows_pay_on_arrival': room_type.allows_pay_on_arrival,
            'is_refundable': room_type.is_refundable,
            'allows_pets': room_type.allows_pets,
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

        num_adults   = form.cleaned_data['num_adults']
        num_children = form.cleaned_data['num_children']
        num_infants  = form.cleaned_data['num_infants']
        num_pets     = form.cleaned_data['num_pets']
        billable_occupants = num_adults + num_children
        
        if billable_occupants > car.capacity:
            messages.error(
                request,
                _('This vehicle has a maximum capacity of %(cap)s passengers.')
                % {'cap': car.capacity}
            )
            request.session['booking_prefill'] = request.POST.dict()
            return redirect('cars:detail', slug=slug)

        if num_pets > 0 and not car.allows_pets:
            messages.error(request, _('This vehicle does not allow pets.'))
            request.session['booking_prefill'] = request.POST.dict()
            return redirect('cars:detail', slug=slug)

        pickup  = form.cleaned_data['pickup_date']
        returns = form.cleaned_data['return_date']
        num_days = max((returns - pickup).days, 1)
        original_price_per_day = car.price_per_day
        price_per_day = car.get_display_price()
        total_price = price_per_day * num_days
        original_total = original_price_per_day * num_days

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
            'num_adults': num_adults,
            'num_children': num_children,
            'num_infants': num_infants,
            'num_pets': num_pets,
            'driver_licence_number': form.cleaned_data.get('driver_licence_number', ''),
            'special_requests': form.cleaned_data.get('special_requests', ''),
            'price_per_day': str(price_per_day),
            'original_price_per_day': str(original_price_per_day),
            'total_price': str(total_price),
            'original_total': str(original_total),
            'discount_percent': car.discount_percent,
            'has_discount': car.has_active_discount,
            'savings': str(original_total - total_price) if car.has_active_discount else '0',
            'currency': 'USD',
            'created_at': str(timezone.now()),
            'allows_pay_on_arrival': car.allows_pay_on_arrival,
            'is_refundable': car.is_refundable,
            'allows_pets': car.allows_pets,
        }

        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/book/summary/pending/')

        return redirect('bookings:summary', reference='pending')


# ---------------------------------------------------------------------------
# Tour Booking
# ---------------------------------------------------------------------------
class TourBookingView(View):

    def post(self, request, slug, *args, **kwargs):
        tour = get_object_or_404(TourPackage, slug=slug, is_active=True)
        form = TourBookingForm(request.POST)

        if not form.is_valid():
            request.session['booking_form_errors'] = form.errors.as_json()
            request.session['booking_prefill'] = request.POST.dict()
            return redirect('tours:detail', slug=slug)

        num_adults      = form.cleaned_data['num_adults']
        num_children    = form.cleaned_data['num_children']
        num_infants     = form.cleaned_data['num_infants']
        num_pets        = form.cleaned_data['num_pets']
        num_participants = num_adults + num_children

        if num_participants > tour.group_size_max:
            messages.error(
                request,
                _('This tour accommodates a maximum of %(max)s participants.')
                % {'max': tour.group_size_max}
            )
            request.session['booking_prefill'] = request.POST.dict()
            return redirect('tours:detail', slug=slug)

        if num_pets > 0 and not tour.allows_pets:
            messages.error(request, _('This tour does not allow pets.'))
            request.session['booking_prefill'] = request.POST.dict()
            return redirect('tours:detail', slug=slug)

        preferred_date = form.cleaned_data['preferred_date']
        original_price_per_person = tour.price_per_person
        price_per_person = tour.get_display_price()
        total_price = price_per_person * num_participants
        original_total = original_price_per_person * num_participants

        request.session[SESSION_BOOKING_KEY] = {
            'service_type': 'tour',
            'tour_id': tour.id,
            'tour_name': tour.get_name(request.LANGUAGE_CODE),
            'tour_slug': tour.slug,
            'tour_type': tour.tour_type,
            'tour_type_display': tour.get_tour_type_display(),
            'duration_days': tour.duration_days,
            'preferred_date': str(preferred_date),
            'num_adults': num_adults,
            'num_children': num_children,
            'num_infants': num_infants,
            'num_pets': num_pets,
            'num_participants': num_participants,
            'special_requests': form.cleaned_data.get('special_requests', ''),
            'price_per_person': str(price_per_person),
            'original_price_per_person': str(original_price_per_person),
            'total_price': str(total_price),
            'original_total': str(original_total),
            'discount_percent': tour.discount_percent,
            'has_discount': tour.has_active_discount,
            'savings': str(original_total - total_price) if tour.has_active_discount else '0',
            'currency': 'USD',
            'created_at': str(timezone.now()),
            'allows_pay_on_arrival': tour.allows_pay_on_arrival,
            'is_refundable': tour.is_refundable,
            'allows_pets': tour.allows_pets,
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
            async_task('apps.bookings.tasks.send_poa_booking_confirmation_customer', booking.id)
            async_task('apps.bookings.tasks.send_poa_booking_notification_admin', booking.id)
            return redirect('bookings:confirmation', reference=booking.reference)

        # pay_now → go to payment options page where PesaPal redirect happens
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
            hotel     = get_object_or_404(Hotel, id=data['hotel_id'])
            room_type = get_object_or_404(HotelRoomType, id=data['room_type_id'])
            if payment_mode == 'pay_on_arrival' and not room_type.allows_pay_on_arrival:
                payment_mode = 'pay_now'
            kwargs.update({
                'hotel': hotel,
                'room_type': room_type,
                'check_in_date': date.fromisoformat(data['check_in_date']),
                'check_out_date': date.fromisoformat(data['check_out_date']),
                'num_rooms': data['num_rooms'],
                'num_adults': data['num_adults'],
                'num_children': data['num_children'],
                'num_infants': data['num_infants'],
                'num_pets': data['num_pets'],
                'num_guests': data['num_guests'],
                'base_price': Decimal(data['price_per_night']),
                'is_refundable': room_type.is_refundable,
                'allows_pets': room_type.allows_pets,
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
                'num_adults': data['num_adults'],
                'num_children': data['num_children'],
                'num_infants': data['num_infants'],
                'num_pets': data['num_pets'],
                'driver_licence_number': data.get('driver_licence_number', ''),
                'base_price': Decimal(data['price_per_day']),
                'is_refundable': car.is_refundable,
                'allows_pets': car.allows_pets,
            })

        elif service_type == 'tour':
            tour = get_object_or_404(TourPackage, id=data['tour_id'])
            if payment_mode == 'pay_on_arrival' and not tour.allows_pay_on_arrival:
                payment_mode = 'pay_now'
            kwargs.update({
                'tour_package': tour,
                'preferred_date': date.fromisoformat(data['preferred_date']),
                'num_participants': data['num_participants'],
                'num_adults': data['num_adults'],
                'num_children': data['num_children'],
                'num_infants': data['num_infants'],
                'num_pets': data['num_pets'],
                'base_price': Decimal(data['price_per_person']),
                'is_refundable': tour.is_refundable,
                'allows_pets': tour.allows_pets,
            })

        kwargs['payment_mode'] = payment_mode
        return Booking.objects.create(**kwargs)


# ---------------------------------------------------------------------------
# Payment Options — initiates PesaPal redirect
# ---------------------------------------------------------------------------
class PaymentOptionsView(LoginRequiredMixin, View):
    template_name = 'bookings/payment_options.html'
    login_url = '/accounts/login/'

    def get(self, request, reference, *args, **kwargs):
        booking = get_object_or_404(
            Booking.objects.select_related('user', 'hotel', 'room_type', 'tour_package', 'car'),
            reference=reference,
            user=request.user,
        )

        # Guard: if already paid, skip straight to confirmation
        if booking.payment_status == 'paid':
            return redirect('bookings:confirmation', reference=booking.reference)

        # Guard: if payment_mode somehow ended up as pay_on_arrival, redirect
        if booking.payment_mode == 'pay_on_arrival':
            return redirect('bookings:confirmation', reference=booking.reference)

        from .pesapal import submit_order_request

        try:
            redirect_url = submit_order_request(booking)
            return redirect(redirect_url)
        except Exception as exc:
            logger.exception(
                'PesaPal submit_order_request failed — booking %s — %s',
                reference, exc
            )
            messages.error(
                request,
                _('We could not connect to the payment gateway. Please try again or contact support.')
            )
            return render(request, self.template_name, {
                'booking': booking,
                'payment_error': True,
            })


# ---------------------------------------------------------------------------
# Booking Confirmation — reads DB state only, never URL params
# ---------------------------------------------------------------------------
class BookingConfirmationView(LoginRequiredMixin, View):
    template_name = 'bookings/booking_confirmation.html'
    login_url = '/accounts/login/'

    def get(self, request, reference, *args, **kwargs):
        booking = get_object_or_404(
            Booking.objects.select_related('hotel', 'room_type', 'tour_package', 'car', 'user'),
            reference=reference,
            user=request.user,
        )

        # PesaPal redirects customer here with OrderTrackingId in query params.
        # This is the fallback verification path for when IPN is delayed or missed.
        # IPN is the primary path — this handles the gap between customer return
        # and IPN arrival (can be seconds to minutes).
        order_tracking_id = request.GET.get('OrderTrackingId', '').strip()

        if (order_tracking_id and booking.payment_mode == 'pay_now'and booking.payment_status == 'pending'):
            from .pesapal import get_transaction_status
            from django_q.tasks import async_task
            try:
                status_data = get_transaction_status(order_tracking_id)
                payment_status_desc = status_data.get('payment_status_description', '').strip()

                if payment_status_desc == 'Completed':
                    booking.payment_status = 'paid'
                    booking.pesapal_tracking_id = order_tracking_id
                    if booking.service_type in ('hotel', 'car'):
                        booking.status = 'confirmed'
                    booking.save(update_fields=[
                        'payment_status', 'pesapal_tracking_id', 'status'
                    ])
                    logger.info(
                        'BookingConfirmationView: payment verified via callback — '
                        'booking %s confirmed', reference
                    )
                    async_task(
                        'apps.bookings.tasks.send_paynow_booking_confirmation_customer',
                        booking.id
                    )
                    async_task(
                        'apps.bookings.tasks.send_paynow_booking_notification_admin',
                        booking.id
                    )

                elif payment_status_desc in ('Failed', 'Invalid'):
                    booking.payment_status = 'failed'
                    booking.save(update_fields=['payment_status'])
                    logger.warning(
                        'BookingConfirmationView: payment failed — booking %s — status %s',
                        reference, payment_status_desc
                    )

            except Exception as exc:
                # Verification failed — show pending state, IPN will update later
                logger.exception(
                    'BookingConfirmationView: get_transaction_status failed — '
                    'booking %s — %s', reference, exc
                )

        return render(request, self.template_name, {'booking': booking})


# ---------------------------------------------------------------------------
# PesaPal IPN Callback
# ---------------------------------------------------------------------------
@csrf_exempt
def pesapal_callback(request):
    """
    PesaPal IPN callback — handles GET requests.

    PesaPal sends IPN as GET with query parameters (ipn_notification_type='GET'
    as registered). The callback_url redirect also arrives as GET.

    PesaPal docs require the IPN endpoint to respond with this exact JSON:
        {"orderNotificationType":"IPNCHANGE",
         "orderTrackingId":"...",
         "orderMerchantReference":"...",
         "status": 200}

    The callback_url (customer redirect after payment) also hits this endpoint
    with OrderNotificationType='CALLBACKURL'. We handle both cases identically —
    verify status via GetTransactionStatus, update DB, queue emails.

    Security: NEVER trust these params to determine payment outcome.
    ALWAYS call get_transaction_status() for independent verification.
    """
    import json
    from django_q.tasks import async_task
    from .pesapal import get_transaction_status

    # PesaPal sends camelCase query params
    order_tracking_id  = request.GET.get('OrderTrackingId', '').strip()
    merchant_reference = request.GET.get('OrderMerchantReference', '').strip()
    notification_type  = request.GET.get('OrderNotificationType', '').strip()

    logger.info(
        'PesaPal callback received — tracking_id=%s  reference=%s  type=%s',
        order_tracking_id, merchant_reference, notification_type
    )

    def _ipn_response(tracking_id, reference, status_code):
        """Build the JSON response PesaPal expects from the IPN endpoint."""
        return HttpResponse(
            json.dumps({
                'orderNotificationType': 'IPNCHANGE',
                'orderTrackingId': tracking_id,
                'orderMerchantReference': reference,
                'status': status_code,
            }),
            content_type='application/json',
            status=200,   # always HTTP 200 — PesaPal retries on anything else
        )

    if not order_tracking_id or not merchant_reference:
        logger.warning('PesaPal callback missing required fields — ignoring')
        return _ipn_response('', '', 200)

    # Customer redirect (callback_url) — just verify and let confirmation page handle UI
    # IPN (ipn_notification_type) — same verification, then update DB and queue emails
    # Both go through the same code path.

    try:
        booking = Booking.objects.select_related('user').get(
            reference=merchant_reference
        )
    except Booking.DoesNotExist:
        logger.error(
            'PesaPal callback — booking not found for reference %s', merchant_reference
        )
        return _ipn_response(order_tracking_id, merchant_reference, 200)

    # Idempotency guard — IPN can fire multiple times
    if booking.payment_status == 'paid':
        logger.info(
            'PesaPal callback — booking %s already paid — skipping', merchant_reference
        )
        if notification_type == 'CALLBACKURL':
            return redirect('bookings:confirmation', reference=booking.reference)
        return _ipn_response(order_tracking_id, merchant_reference, 200)

    # Independent status verification — mandatory per PesaPal docs
    try:
        status_data = get_transaction_status(order_tracking_id)
    except Exception as exc:
        logger.exception(
            'PesaPal callback — get_transaction_status failed — tracking_id %s — %s',
            order_tracking_id, exc
        )
        if notification_type == 'CALLBACKURL':
            return redirect('bookings:confirmation', reference=booking.reference)
        return _ipn_response(order_tracking_id, merchant_reference, 500)

    payment_status_desc = status_data.get('payment_status_description', '').strip()
    logger.info(
        'PesaPal callback — booking %s — verified status: %s',
        merchant_reference, payment_status_desc
    )

    if payment_status_desc == 'Completed':
        booking.payment_status      = 'paid'
        booking.pesapal_tracking_id = order_tracking_id
        # Tours stay pending_confirmation — admin must manually confirm tour date
        # Hotels and cars move directly to confirmed after payment
        if booking.service_type in ('hotel', 'car'):
            booking.status = 'confirmed'
        booking.save(update_fields=['payment_status', 'pesapal_tracking_id', 'status'])

        logger.info(
            'PesaPal callback — booking %s confirmed — status=%s',
            merchant_reference, booking.status
        )

        async_task(
            'apps.bookings.tasks.send_paynow_booking_confirmation_customer', booking.id
        )
        async_task(
            'apps.bookings.tasks.send_paynow_booking_notification_admin', booking.id
        )

    elif payment_status_desc in ('Failed', 'Invalid'):
        booking.payment_status = 'failed'
        booking.save(update_fields=['payment_status'])
        logger.warning(
            'PesaPal callback — payment failed — booking %s — status: %s',
            merchant_reference, payment_status_desc
        )

    else:
        # 'Reversed' or unexpected value — log, wait for next IPN
        logger.info(
            'PesaPal callback — unactioned status "%s" for booking %s',
            payment_status_desc, merchant_reference
        )

    # Customer redirect: send them to the confirmation page
    if notification_type == 'CALLBACKURL':
        return redirect('bookings:confirmation', reference=booking.reference)

    # IPN: respond with the JSON PesaPal expects
    return _ipn_response(order_tracking_id, merchant_reference, 200)
