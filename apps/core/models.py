from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models import Q, UniqueConstraint


class SavedFavourite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favourites',
    )
    hotel = models.ForeignKey(
        'hotels.Hotel', on_delete=models.CASCADE, null=True, blank=True
    )
    tour_package = models.ForeignKey(
        'tours.TourPackage', on_delete=models.CASCADE, null=True, blank=True
    )
    car = models.ForeignKey(
        'cars.CarRental', on_delete=models.CASCADE, null=True, blank=True
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Saved Favourite')
        verbose_name_plural = _('Saved Favourites')
        constraints = [
            UniqueConstraint(
                fields=['user', 'hotel'],
                condition=Q(hotel__isnull=False),
                name='unique_user_hotel_favourite'
            ),
            UniqueConstraint(
                fields=['user', 'tour_package'],
                condition=Q(tour_package__isnull=False),
                name='unique_user_tour_favourite'
            ),
            UniqueConstraint(
                fields=['user', 'car'],
                condition=Q(car__isnull=False),
                name='unique_user_car_favourite'
            ),
        ]

    def __str__(self):
        item = self.hotel or self.tour_package or self.car
        return f"{self.user} — {item}"