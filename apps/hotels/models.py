from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Hotel(models.Model):

    LOCATION_CHOICES = [
        ('zanzibar', _('Zanzibar')),
        ('dar_es_salaam', _('Dar es Salaam')),
    ]

    APPROVAL_CHOICES = [
        ('pending', _('Pending Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    STAR_CHOICES = [(i, str(i)) for i in range(1, 6)]

    name = models.CharField(max_length=200, verbose_name=_('Hotel Name'))
    slug = models.SlugField(unique=True, blank=True)
    location = models.CharField(
        max_length=20, choices=LOCATION_CHOICES, verbose_name=_('Location')
    )

    description_en = models.TextField(verbose_name=_('Description (English)'))
    description_fr = models.TextField(blank=True, null=True, verbose_name=_('Description (French)'))
    description_ru = models.TextField(blank=True, null=True, verbose_name=_('Description (Russian)'))

    stars = models.IntegerField(choices=STAR_CHOICES, verbose_name=_('Star Rating'))
    price_per_night = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_('Price Per Night (USD)')
    )
    address = models.CharField(max_length=300, verbose_name=_('Address'))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    tripadvisor_url = models.URLField(blank=True, null=True, verbose_name=_('TripAdvisor URL'))

    # Ownership & approval
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='hotels_created',
        verbose_name=_('Created By'),
    )
    approval_status = models.CharField(
        max_length=10, choices=APPROVAL_CHOICES, default='pending',
        verbose_name=_('Approval Status')
    )
    rejection_reason = models.TextField(blank=True, null=True, verbose_name=_('Rejection Reason'))
    is_active = models.BooleanField(default=False, verbose_name=_('Active / Visible'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Hotel')
        verbose_name_plural = _('Hotels')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Hotel.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_description(self, lang='en'):
        return getattr(self, f'description_{lang}', None) or self.description_en

    @property
    def cover_photo(self):
        return self.photos.filter(is_cover=True).first() or self.photos.first()

    @property
    def is_publicly_visible(self):
        return self.is_active and self.approval_status == 'approved'


class HotelPhoto(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='hotels/photos/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    is_cover = models.BooleanField(default=False, verbose_name=_('Cover Photo'))
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Photo for {self.hotel.name}"


class HotelRoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types')
    name = models.CharField(max_length=100, verbose_name=_('Room Type Name'))
    description_en = models.TextField(verbose_name=_('Description (English)'))
    description_fr = models.TextField(blank=True, null=True)
    description_ru = models.TextField(blank=True, null=True)
    price_per_night = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        verbose_name=_('Price Per Night (USD) — overrides hotel base price if set')
    )
    max_guests = models.PositiveIntegerField(verbose_name=_('Max Guests Per Room'))
    amenities = models.JSONField(
        default=list,
        verbose_name=_('Amenities'),
        help_text=_('List of amenity strings e.g. ["WiFi", "AC", "Pool view"]')
    )
    is_available = models.BooleanField(default=True)

    # Discount
    discount_percent = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Discount (%)'),
        help_text=_('0 = no discount. Applied to the effective price per night.')
    )
    discount_expires_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('Discount Expires At'),
        help_text=_('Leave blank for a permanent discount.')
    )

    # Booking policy
    is_refundable = models.BooleanField(
        default=True,
        verbose_name=_('Refundable'),
        help_text=_('If unchecked, non-refundable regardless of cancellation policy.')
    )
    allows_pay_on_arrival = models.BooleanField(
        default=True,
        verbose_name=_('Allows Pay on Arrival'),
        help_text=_('If unchecked, only Pay Now is accepted for this room type.')
    )
    allows_pets = models.BooleanField(
        default=False,
        verbose_name=_('Pets Allowed'),
        help_text=_('If unchecked, pets are not permitted in this room type.')
    )

    class Meta:
        verbose_name = _('Room Type')
        verbose_name_plural = _('Room Types')
        ordering = ['price_per_night']

    def __str__(self):
        return f"{self.hotel.name} — {self.name}"

    def get_effective_price(self):
        return self.price_per_night or self.hotel.price_per_night

    def get_discounted_price(self):
        from django.utils import timezone
        from decimal import Decimal

        if not self.discount_percent or self.discount_percent <= 0:
            return None
        if self.discount_expires_at and self.discount_expires_at < timezone.now():
            return None
        base = self.get_effective_price()
        factor = Decimal(1) - Decimal(self.discount_percent) / Decimal(100)
        return (base * factor).quantize(Decimal('0.01'))

    def get_display_price(self):
        return self.get_discounted_price() or self.get_effective_price()

    @property
    def has_active_discount(self):
        return self.get_discounted_price() is not None

    @property
    def cover_photo(self):
        """First photo by order — no is_cover concept for room type photos."""
        return self.room_photos.first()


class HotelRoomTypePhoto(models.Model):
    """
    Photos scoped to a specific room type.
    No is_cover field — cover is simply the first photo by order.
    Same AJAX upload/delete/reorder pattern as HotelPhoto and TourPhoto.
    """
    room_type = models.ForeignKey(
        HotelRoomType,
        on_delete=models.CASCADE,
        related_name='room_photos',
    )
    image = models.ImageField(upload_to='hotels/room_photos/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Room Type Photo')
        verbose_name_plural = _('Room Type Photos')
        ordering = ['order']

    def __str__(self):
        return f"Photo for {self.room_type.hotel.name} — {self.room_type.name}"