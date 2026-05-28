from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


def generate_booking_reference():
    from django.apps import apps
    from django.utils import timezone
    year = timezone.now().year
    BookingModel = apps.get_model('bookings', 'Booking')
    last = BookingModel.objects.order_by('id').last()
    next_num = (last.id + 1) if last else 1
    return f"JDV-{year}-{str(next_num).zfill(5)}"


class CancellationPolicy(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('hotel', _('Hotel')),
        ('tour', _('Safari & Tour')),
        ('car', _('Car Rental')),
    ]

    service_type = models.CharField(max_length=10, choices=SERVICE_TYPE_CHOICES)
    days_before_service = models.PositiveIntegerField(
        verbose_name=_('Minimum Days Before Service'),
        help_text=_('Cancellation must be made at least this many days before service date')
    )
    refund_percentage = models.PositiveIntegerField(
        verbose_name=_('Refund Percentage'),
        help_text=_('0 = no refund, 50 = half, 100 = full refund')
    )
    label_en = models.CharField(max_length=200, verbose_name=_('Label (English)'))
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Cancellation Policy')
        verbose_name_plural = _('Cancellation Policies')
        ordering = ['service_type', '-days_before_service']

    def __str__(self):
        return f"{self.get_service_type_display()} — {self.refund_percentage}% refund (≥{self.days_before_service} days)"


class Booking(models.Model):

    SERVICE_TYPE_CHOICES = [
        ('hotel', _('Hotel')),
        ('tour', _('Safari & Tour')),
        ('car', _('Car Rental')),
    ]

    PAYMENT_MODE_CHOICES = [
        ('pay_now', _('Pay Now (Online)')),
        ('pay_on_arrival', _('Pay on Arrival')),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('refunded', _('Refunded')),
        ('failed', _('Failed')),
    ]

    STATUS_CHOICES = [
        ('pending_confirmation', _('Pending Confirmation')),
        ('confirmed', _('Confirmed')),
        ('cancellation_requested', _('Cancellation Requested')),
        ('cancelled', _('Cancelled')),
        ('completed', _('Completed')),
        ('no_show', _('No Show')),
    ]

    CURRENCY_CHOICES = [
        ('USD', 'USD'),
        ('TZS', 'TZS'),
        ('EUR', 'EUR'),
    ]

    RENTAL_MODE_CHOICES = [
        ('self_drive', _('Self Drive')),
        ('with_driver', _('With Driver')),
    ]

    # Core
    reference = models.CharField(
        max_length=20, unique=True, default=generate_booking_reference,
        verbose_name=_('Booking Reference')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='bookings',
    )
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPE_CHOICES)

    # Service links — only one populated per booking
    hotel = models.ForeignKey(
        'hotels.Hotel', on_delete=models.PROTECT, null=True, blank=True,
        related_name='bookings'
    )
    room_type = models.ForeignKey(
        'hotels.HotelRoomType', on_delete=models.PROTECT, null=True, blank=True
    )
    tour_package = models.ForeignKey(
        'tours.TourPackage', on_delete=models.PROTECT, null=True, blank=True,
        related_name='bookings'
    )
    car = models.ForeignKey(
        'cars.CarRental', on_delete=models.PROTECT, null=True, blank=True,
        related_name='bookings'
    )

    # Dates
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    preferred_date = models.DateField(null=True, blank=True)
    pickup_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)

    # -----------------------------------------------------------------------
    # Guests / participants — granular breakdown
    # All nullable: only the fields relevant to the service_type are populated.
    # -----------------------------------------------------------------------
    num_adults = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name=_('Adults'),
    )
    num_children = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name=_('Children (2–12)'),
    )
    num_infants = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name=_('Infants (under 2)'),
    )
    num_pets = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name=_('Pets'),
    )

    # Hotels only — how many rooms of the selected type
    num_rooms = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name=_('Number of Rooms'),
    )

    # Legacy aggregate field — kept for backward compat; now a DB column
    # populated from num_adults + num_children + num_infants at create time.
    # Do NOT use this for price calculation — use num_rooms × nights for hotels.
    num_guests = models.PositiveIntegerField(null=True, blank=True)

    # Tours — total headcount (adults + children; infants typically free)
    num_participants = models.PositiveIntegerField(null=True, blank=True)

    # Cars — computed from pickup/return dates
    num_days = models.PositiveIntegerField(null=True, blank=True)

    # Car-specific
    pickup_location = models.CharField(max_length=200, blank=True, null=True)
    rental_mode = models.CharField(
        max_length=15, choices=RENTAL_MODE_CHOICES, blank=True, null=True
    )
    driver_licence_number = models.CharField(max_length=50, blank=True, null=True)

    # Pricing — snapshotted at booking time, never recalculated
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')

    # Payment
    payment_mode = models.CharField(max_length=15, choices=PAYMENT_MODE_CHOICES)
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending'
    )
    pesapal_order_id = models.CharField(max_length=100, blank=True, null=True)
    pesapal_tracking_id = models.CharField(max_length=100, blank=True, null=True)

    # Lifecycle
    status = models.CharField(
        max_length=25, choices=STATUS_CHOICES, default='pending_confirmation'
    )
    special_requests = models.TextField(blank=True, null=True)
    is_refundable = models.BooleanField(
        default=True,
        verbose_name=_('Is Refundable'),
        help_text=_('Snapshotted from listing at booking time. False = non-refundable regardless of policy.')
    )
    # Snapshotted from listing at booking time
    allows_pets = models.BooleanField(
        default=False,
        verbose_name=_('Pets Allowed'),
        help_text=_('Snapshotted from listing at booking time.')
    )
    cancellation_reason = models.TextField(blank=True, null=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cancellations_made',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} — {self.user}"

    @property
    def service_date(self):
        """Primary date used for cancellation window calculation."""
        return self.check_in_date or self.preferred_date or self.pickup_date

    @property
    def nights(self):
        """Number of nights for hotel bookings."""
        if self.check_in_date and self.check_out_date:
            return (self.check_out_date - self.check_in_date).days
        return None

    @property
    def total_occupants(self):
        """Total people across adults + children + infants."""
        return (self.num_adults or 0) + (self.num_children or 0) + (self.num_infants or 0)