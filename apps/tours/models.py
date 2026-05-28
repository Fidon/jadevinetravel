from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class TourPackage(models.Model):

    TOUR_TYPE_CHOICES = [
        ('safari', _('Safari')),
        ('beach', _('Beach')),
        ('cultural', _('Cultural')),
        ('climbing', _('Climbing')),
        ('combined', _('Combined Safari & Beach')),
    ]

    name_en = models.CharField(max_length=200, verbose_name=_('Name (English)'))
    name_fr = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('Name (French)'))
    name_ru = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('Name (Russian)'))
    slug = models.SlugField(unique=True, blank=True)
    tour_type = models.CharField(
        max_length=20, choices=TOUR_TYPE_CHOICES, verbose_name=_('Tour Type')
    )

    description_en = models.TextField(verbose_name=_('Description (English)'))
    description_fr = models.TextField(blank=True, null=True)
    description_ru = models.TextField(blank=True, null=True)

    duration_days = models.PositiveIntegerField(verbose_name=_('Duration (Days)'))
    group_size_max = models.PositiveIntegerField(verbose_name=_('Maximum Group Size'))
    price_per_person = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_('Price Per Person (USD)')
    )

    highlights_en = models.JSONField(default=list, verbose_name=_('Highlights (English)'))
    highlights_fr = models.JSONField(default=list, blank=True, null=True)
    highlights_ru = models.JSONField(default=list, blank=True, null=True)

    inclusions_en = models.JSONField(default=list, verbose_name=_('Inclusions (English)'))
    inclusions_fr = models.JSONField(default=list, blank=True, null=True)
    inclusions_ru = models.JSONField(default=list, blank=True, null=True)

    exclusions_en = models.JSONField(default=list, verbose_name=_('Exclusions (English)'))
    exclusions_fr = models.JSONField(default=list, blank=True, null=True)
    exclusions_ru = models.JSONField(default=list, blank=True, null=True)

    what_to_bring_en = models.TextField(blank=True, null=True)
    what_to_bring_fr = models.TextField(blank=True, null=True)
    what_to_bring_ru = models.TextField(blank=True, null=True)

    cover_image = models.ImageField(upload_to='tours/covers/')
    is_active = models.BooleanField(default=True, verbose_name=_('Active / Visible'))
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('Featured'),
        help_text=_('Show in Featured Packages section on homepage')
    )

    # Discount
    discount_percent = models.PositiveSmallIntegerField(default=0, verbose_name=_('Discount (%)'))
    discount_expires_at = models.DateTimeField(blank=True, null=True)

    # Booking policy
    is_refundable = models.BooleanField(default=True, verbose_name=_('Refundable'))
    allows_pay_on_arrival = models.BooleanField(default=True, verbose_name=_('Allows Pay on Arrival'))
    allows_pets = models.BooleanField(
        default=False,
        verbose_name=_('Pets Allowed'),
        help_text=_('If unchecked, pets are not permitted on this tour.')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Tour Package')
        verbose_name_plural = _('Tour Packages')
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.name_en

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name_en)
            slug = base_slug
            counter = 1
            while TourPackage.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_name(self, lang='en'):
        return getattr(self, f'name_{lang}', None) or self.name_en

    def get_description(self, lang='en'):
        return getattr(self, f'description_{lang}', None) or self.description_en

    def get_highlights(self, lang='en'):
        return getattr(self, f'highlights_{lang}', None) or self.highlights_en

    def get_inclusions(self, lang='en'):
        return getattr(self, f'inclusions_{lang}', None) or self.inclusions_en

    def get_exclusions(self, lang='en'):
        return getattr(self, f'exclusions_{lang}', None) or self.exclusions_en

    def get_discounted_price(self):
        from django.utils import timezone
        from decimal import Decimal

        if not self.discount_percent or self.discount_percent <= 0:
            return None
        if self.discount_expires_at and self.discount_expires_at < timezone.now():
            return None
        factor = Decimal(1) - Decimal(self.discount_percent) / Decimal(100)
        return (self.price_per_person * factor).quantize(Decimal('0.01'))

    def get_display_price(self):
        return self.get_discounted_price() or self.price_per_person

    @property
    def has_active_discount(self):
        return self.get_discounted_price() is not None


class TourItineraryDay(models.Model):
    package = models.ForeignKey(
        TourPackage, on_delete=models.CASCADE, related_name='itinerary_days'
    )
    day_number = models.PositiveIntegerField(verbose_name=_('Day Number'))
    title_en = models.CharField(max_length=200, verbose_name=_('Title (English)'))
    title_fr = models.CharField(max_length=200, blank=True, null=True)
    title_ru = models.CharField(max_length=200, blank=True, null=True)
    description_en = models.TextField(verbose_name=_('Description (English)'))
    description_fr = models.TextField(blank=True, null=True)
    description_ru = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['day_number']
        unique_together = ['package', 'day_number']

    def __str__(self):
        return f"{self.package.name_en} — Day {self.day_number}"

    def get_title(self, lang='en'):
        return getattr(self, f'title_{lang}', None) or self.title_en

    def get_description(self, lang='en'):
        return getattr(self, f'description_{lang}', None) or self.description_en


class TourPhoto(models.Model):
    package = models.ForeignKey(
        TourPackage, on_delete=models.CASCADE, related_name='photos'
    )
    image = models.ImageField(upload_to='tours/photos/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']