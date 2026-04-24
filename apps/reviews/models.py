from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):

    SERVICE_TYPE_CHOICES = [
        ('hotel', _('Hotel')),
        ('tour', _('Safari & Tour')),
        ('car', _('Car Rental')),
    ]

    STATUS_CHOICES = [
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    # Who wrote it and which booking it relates to
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='review',
        help_text=_('One review per booking — enforced at DB level.')
    )

    # What service is being reviewed
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPE_CHOICES)
    hotel = models.ForeignKey(
        'hotels.Hotel',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='reviews',
    )
    tour_package = models.ForeignKey(
        'tours.TourPackage',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='reviews',
    )
    car = models.ForeignKey(
        'cars.CarRental',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='reviews',
    )

    # The review itself
    rating = models.PositiveSmallIntegerField(
        verbose_name=_('Rating (1–10)'),
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    comment = models.TextField(
        blank=True, null=True,
        verbose_name=_('Comment'),
    )

    # Moderation — requires Super Admin or listing Mini-Admin approval
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Moderation Status'),
    )
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviews_moderated',
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.CharField(
        max_length=300,
        blank=True, null=True,
        verbose_name=_('Rejection Reason'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user} — {self.rating}/10 ({self.get_service_type_display()})"

    @property
    def is_approved(self):
        return self.status == 'approved'