"""
apps/core/sitemaps.py

i18n sitemaps. With i18n=True / alternates=True / x_default=True, Django emits one
<url> per (page x language) plus reciprocal <xhtml:link hreflang> alternates and an
x-default — exactly what Google wants for a 3-language site.

CRITICAL: location() returns reverse(), never a hardcoded path. The framework calls
location() once per language under translation.override(), and reverse() respects
prefix_default_language=False (en unprefixed, fr/ru prefixed). A hardcoded string
would return the same URL for all three languages and silently break the alternates.

The host comes from the Sites framework (Site.objects.get_current().domain) — make
sure it is set to jadevinetravel.com in prod (the one-line shell command from the
settings step). protocol is forced to https.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.hotels.models import Hotel
from apps.tours.models import TourPackage
from apps.cars.models import CarRental


class StaticViewSitemap(Sitemap):
    protocol = 'https'
    i18n = True
    alternates = True
    x_default = True
    changefreq = 'weekly'

    def items(self):
        return [
            'core:home',
            'hotels:list',
            'tours:list',
            'cars:list',
            'gallery:gallery',
            'core:about',
            'contact:contact',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        # Homepage is the strongest internal signal; landing/listing pages next.
        return 1.0 if item == 'core:home' else 0.7


class _ListingSitemap(Sitemap):
    """Shared config for the three bookable-listing sitemaps."""
    protocol = 'https'
    i18n = True
    alternates = True
    x_default = True
    changefreq = 'weekly'
    priority = 0.9

    def lastmod(self, obj):
        return obj.updated_at


class HotelSitemap(_ListingSitemap):
    def items(self):
        # Mirror the public queryset: active + approved only.
        return Hotel.objects.filter(is_active=True, approval_status='approved')

    def location(self, obj):
        return reverse('hotels:detail', kwargs={'slug': obj.slug})


class TourSitemap(_ListingSitemap):
    def items(self):
        return TourPackage.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('tours:detail', kwargs={'slug': obj.slug})


class CarSitemap(_ListingSitemap):
    def items(self):
        return CarRental.objects.filter(
            is_active=True, is_available=True, approval_status='approved'
        )

    def location(self, obj):
        return reverse('cars:detail', kwargs={'slug': obj.slug})


# Registered in config/urls.py
sitemaps = {
    'static': StaticViewSitemap,
    'hotels': HotelSitemap,
    'tours': TourSitemap,
    'cars': CarSitemap,
}