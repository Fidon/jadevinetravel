import json
from django.views.generic import DetailView
from django.views import View
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404, render
from .models import Hotel, HotelRoomType
from apps.reviews.models import Review
from django.db.models import Avg, Count


# ---------------------------------------------------------------------------
# Public queryset helper — never expose unapproved/inactive hotels
# ---------------------------------------------------------------------------
def public_hotels_qs():
    return Hotel.objects.filter(
        is_active=True,
        approval_status='approved'
    ).prefetch_related('photos', 'room_types')


# ---------------------------------------------------------------------------
# Hotel List — renders initial page; AJAX endpoint on same URL via GET param
# ---------------------------------------------------------------------------
class HotelListView(View):
    template_name = 'hotels/hotel_list.html'

    def get(self, request, *args, **kwargs):
        # If AJAX filter request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self._ajax_filter(request)
        # Initial page render — no hotels in context, jQuery loads them via AJAX
        return render(request, self.template_name, {
            'page_title': _('Hotels in Zanzibar & Dar es Salaam'),
        })

    def _ajax_filter(self, request):
        qs = public_hotels_qs()

        location = request.GET.get('location', '').strip()
        stars = request.GET.get('stars', '').strip()
        min_price = request.GET.get('min_price', '').strip()
        max_price = request.GET.get('max_price', '').strip()
        guests = request.GET.get('guests', '').strip()

        if location:
            qs = qs.filter(location=location)
        if stars:
            try:
                qs = qs.filter(stars=int(stars))
            except ValueError:
                pass
        if min_price:
            try:
                qs = qs.filter(price_per_night__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                qs = qs.filter(price_per_night__lte=float(max_price))
            except ValueError:
                pass
        if guests:
            try:
                # Filter hotels that have at least one room type accommodating N guests
                guest_count = int(guests)
                qs = qs.filter(room_types__max_guests__gte=guest_count).distinct()
            except ValueError:
                pass

        lang = request.LANGUAGE_CODE

        hotels_data = []
        for hotel in qs:
            cover = hotel.cover_photo

            # Rating — only shown when 3+ approved reviews
            review_data = Review.objects.filter(
                hotel=hotel,
                status='approved'
            ).aggregate(avg=Avg('rating'), total=Count('id'))
            avg_rating   = round(review_data['avg'], 1) if review_data['avg'] and review_data['total'] >= 3 else None
            review_count = review_data['total'] if review_data['total'] >= 3 else 0

            # Lowest active discount across room types (for card display)
            best_discount = 0
            for rt in hotel.room_types.all():
                if rt.has_active_discount and rt.discount_percent > best_discount:
                    best_discount = rt.discount_percent

            # Best discounted price across room types for card display
            best_display_price = str(hotel.price_per_night)
            if best_discount > 0:
                from decimal import Decimal
                factor = Decimal(1) - Decimal(best_discount) / Decimal(100)
                best_display_price = str(
                    (hotel.price_per_night * factor).quantize(Decimal('0.01'))
                )

            hotels_data.append({
                'id': hotel.id,
                'name': hotel.name,
                'slug': hotel.slug,
                'location': hotel.get_location_display(),
                'stars': hotel.stars,
                'price_per_night': str(hotel.price_per_night),
                'display_price': best_display_price,
                'description': hotel.get_description(lang)[:150] + '...' if hotel.get_description(lang) else '',
                'cover_photo': cover.image.url if cover else None,
                'tripadvisor_url': hotel.tripadvisor_url or '',
                'has_discount': best_discount > 0,
                'discount_percent': best_discount,
                'avg_rating': avg_rating,
                'review_count': review_count,
                'url': request.build_absolute_uri(f"/hotels/{hotel.slug}/"),
            })

        return JsonResponse({'hotels': hotels_data})


# ---------------------------------------------------------------------------
# Hotel Detail
# ---------------------------------------------------------------------------
class HotelDetailView(DetailView):
    template_name = 'hotels/hotel_detail.html'
    context_object_name = 'hotel'

    def get_object(self):
        return get_object_or_404(
            Hotel.objects.prefetch_related(
                'photos',
                'room_types'
            ),
            slug=self.kwargs['slug'],
            is_active=True,
            approval_status='approved'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel = self.object
        lang = self.request.LANGUAGE_CODE

        # Pass translated description
        context['description'] = hotel.get_description(lang)

        # Rating
        review_data = Review.objects.filter(
            hotel=hotel,
            status='approved'
        ).aggregate(avg=Avg('rating'), total=Count('id'))
        avg_rating = round(review_data['avg'], 1) if review_data['avg'] and review_data['total'] >= 3 else None
        review_count = review_data['total'] if review_data['total'] >= 3 else 0
        context['avg_rating'] = avg_rating
        context['review_count'] = review_count

        # Room types with pricing, discount, and policy
        room_types = []
        for rt in hotel.room_types.filter(is_available=True):
            discounted = rt.get_discounted_price()
            room_types.append({
                'id': rt.id,
                'name': rt.name,
                'description': getattr(rt, f'description_{lang}', None) or rt.description_en,
                'price': str(rt.get_effective_price()),
                'display_price': str(rt.get_display_price()),
                'discounted_price': str(discounted) if discounted else None,
                'has_discount': rt.has_active_discount,
                'discount_percent': rt.discount_percent,
                'max_guests': rt.max_guests,
                'amenities': rt.amenities,
                'is_refundable': rt.is_refundable,
                'allows_pay_on_arrival': rt.allows_pay_on_arrival,
            })
        context['room_types'] = room_types
        context['room_types_json'] = json.dumps(room_types)

        # All photos
        context['photos'] = hotel.photos.all()

        # Booking session data if returning from a failed login redirect
        # (pre-fills the form so user doesn't have to re-enter)
        context['booking_prefill'] = self.request.session.pop('booking_prefill', None)

        return context