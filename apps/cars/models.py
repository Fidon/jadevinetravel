from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class CarRental(models.Model):

    VEHICLE_TYPE_CHOICES = [
        ('sedan', _('Sedan')),
        ('suv', _('SUV')),
        ('minibus', _('Minibus')),
        ('4x4', _('4x4 Safari')),
        ('van', _('Van')),
    ]

    FUEL_CHOICES = [
        ('petrol', _('Petrol')),
        ('diesel', _('Diesel')),
    ]

    TRANSMISSION_CHOICES = [
        ('manual', _('Manual')),
        ('automatic', _('Automatic')),
    ]

    APPROVAL_CHOICES = [
        ('pending', _('Pending Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    name = models.CharField(max_length=200, verbose_name=_('Vehicle Name'))
    slug = models.SlugField(unique=True, blank=True)
    vehicle_type = models.CharField(
        max_length=10, choices=VEHICLE_TYPE_CHOICES, verbose_name=_('Vehicle Type')
    )
    make = models.CharField(max_length=100, verbose_name=_('Make'))
    model = models.CharField(max_length=100, verbose_name=_('Model'))
    year = models.PositiveIntegerField(verbose_name=_('Year'))
    capacity = models.PositiveIntegerField(verbose_name=_('Passenger Capacity'))
    fuel_type = models.CharField(max_length=10, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES)
    price_per_day = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_('Price Per Day (USD)')
    )

    offers_self_drive = models.BooleanField(default=False, verbose_name=_('Offers Self-Drive'))
    offers_driver = models.BooleanField(default=True, verbose_name=_('Offers Driver'))
    driver_speaks_en = models.BooleanField(default=True, verbose_name=_('Driver Speaks English'))
    driver_speaks_fr = models.BooleanField(default=False, verbose_name=_('Driver Speaks French'))

    pickup_locations = models.JSONField(
        default=list,
        verbose_name=_('Pickup Locations'),
        help_text=_('List of location names e.g. ["Zanzibar Airport", "Stone Town"]')
    )

    description_en = models.TextField(blank=True, null=True)
    description_fr = models.TextField(blank=True, null=True)
    description_ru = models.TextField(blank=True, null=True)

    # Ownership & approval
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cars_created',
    )
    approval_status = models.CharField(
        max_length=10, choices=APPROVAL_CHOICES, default='pending'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(
        default=True,
        verbose_name=_('Available for Booking'),
        help_text=_('Toggle off during maintenance')
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_('Active / Visible'),
    )

    # Discount
    discount_percent = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Discount (%)'),
    )
    discount_expires_at = models.DateTimeField(blank=True, null=True)

    # Booking policy
    is_refundable = models.BooleanField(
        default=True,
        verbose_name=_('Refundable'),
    )
    allows_pay_on_arrival = models.BooleanField(
        default=True,
        verbose_name=_('Allows Pay on Arrival'),
    )
    allows_pets = models.BooleanField(
        default=False,
        verbose_name=_('Pets Allowed'),
        help_text=_('If unchecked, pets are not permitted in this vehicle.')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Car Rental')
        verbose_name_plural = _('Car Rentals')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while CarRental.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_description(self, lang='en'):
        return getattr(self, f'description_{lang}', None) or self.description_en

    def get_discounted_price(self):
        from django.utils import timezone
        from decimal import Decimal

        if not self.discount_percent or self.discount_percent <= 0:
            return None
        if self.discount_expires_at and self.discount_expires_at < timezone.now():
            return None
        factor = Decimal(1) - Decimal(self.discount_percent) / Decimal(100)
        return (self.price_per_day * factor).quantize(Decimal('0.01'))

    def get_display_price(self):
        return self.get_discounted_price() or self.price_per_day

    @property
    def has_active_discount(self):
        return self.get_discounted_price() is not None

    @property
    def cover_photo(self):
        return self.photos.filter(is_cover=True).first() or self.photos.first()

    @property
    def is_publicly_visible(self):
        return self.is_active and self.is_available and self.approval_status == 'approved'


class CarPhoto(models.Model):
    car = models.ForeignKey(CarRental, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='cars/photos/')
    is_cover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']