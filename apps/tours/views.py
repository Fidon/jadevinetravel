import json
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from .models import TourPackage


class TourListView(View):
    template_name = 'tours/tour_list.html'

    def get(self, request, *args, **kwargs):
        lang = request.LANGUAGE_CODE
        qs = TourPackage.objects.filter(is_active=True).prefetch_related('photos')

        tour_type = request.GET.get('tour_type', '').strip()
        max_price = request.GET.get('max_price', '').strip()
        max_dur   = request.GET.get('max_duration', '').strip()

        if tour_type and tour_type != 'all':
            qs = qs.filter(tour_type=tour_type)
        if max_price:
            try:
                qs = qs.filter(price_per_person__lte=float(max_price))
            except ValueError:
                pass
        if max_dur:
            try:
                qs = qs.filter(duration_days__lte=int(max_dur))
            except ValueError:
                pass

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = [self._serialize(t, lang) for t in qs]
            return JsonResponse({'tours': data, 'count': len(data)})

        all_tours = TourPackage.objects.filter(is_active=True)
        return render(request, self.template_name, {
            'tour_count': all_tours.count(),
        })

    def _serialize(self, tour, lang):
        from apps.reviews.models import Review
        from django.db.models import Avg, Count

        cover = tour.cover_image.url if tour.cover_image else None

        # Discount
        discounted = tour.get_discounted_price()
        has_discount = discounted is not None

        # Rating — only if 3+ approved reviews
        review_data = Review.objects.filter(
            tour_package=tour,
            status='approved'
        ).aggregate(avg=Avg('rating'), total=Count('id'))
        avg_rating = round(review_data['avg'], 1) if review_data['avg'] and review_data['total'] >= 3 else None
        review_count = review_data['total'] if review_data['total'] >= 3 else 0

        return {
            'id': tour.id,
            'slug': tour.slug,
            'name': tour.get_name(lang),
            'tour_type': tour.tour_type,
            'tour_type_display': tour.get_tour_type_display(),
            'duration_days': tour.duration_days,
            'group_size_max': tour.group_size_max,
            'price_per_person': str(tour.price_per_person),
            'display_price': str(discounted) if has_discount else str(tour.price_per_person),
            'has_discount': has_discount,
            'discount_percent': tour.discount_percent if has_discount else 0,
            'highlights': tour.get_highlights(lang)[:3],
            'cover_image': cover,
            'is_featured': tour.is_featured,
            'allows_pay_on_arrival': tour.allows_pay_on_arrival,
            'is_refundable': tour.is_refundable,
            'avg_rating': avg_rating,
            'review_count': review_count,
            'url': f'/tours/{tour.slug}/',
        }


class TourDetailView(View):
    template_name = 'tours/tour_detail.html'

    def get(self, request, slug, *args, **kwargs):
        from apps.reviews.models import Review
        from django.db.models import Avg, Count

        tour = get_object_or_404(TourPackage, slug=slug, is_active=True)
        lang = request.LANGUAGE_CODE

        itinerary_days = tour.itinerary_days.all()
        photos = tour.photos.all()
        highlights = tour.get_highlights(lang)
        inclusions = tour.get_inclusions(lang)
        exclusions = tour.get_exclusions(lang)
        what_to_bring = getattr(tour, f'what_to_bring_{lang}', None) or tour.what_to_bring_en

        photos_json = json.dumps([
            {'url': p.image.url, 'caption': p.caption or ''}
            for p in photos
        ])

        # Discount
        discounted_price = tour.get_discounted_price()
        display_price = discounted_price or tour.price_per_person

        # Rating
        review_data = Review.objects.filter(
            tour_package=tour,
            status='approved'
        ).aggregate(avg=Avg('rating'), total=Count('id'))
        avg_rating = round(review_data['avg'], 1) if review_data['avg'] and review_data['total'] >= 3 else None
        review_count = review_data['total'] if review_data['total'] >= 3 else 0

        return render(request, self.template_name, {
            'tour': tour,
            'tour_name': tour.get_name(lang),
            'tour_description': tour.get_description(lang),
            'highlights': highlights,
            'inclusions': inclusions,
            'exclusions': exclusions,
            'what_to_bring': what_to_bring,
            'itinerary_days': itinerary_days,
            'photos': photos,
            'photos_json': photos_json,
            'price_per_person': str(tour.price_per_person),
            'display_price': str(display_price),
            'discounted_price': str(discounted_price) if discounted_price else None,
            'has_discount': discounted_price is not None,
            'discount_percent': tour.discount_percent,
            'allows_pay_on_arrival': tour.allows_pay_on_arrival,
            'is_refundable': tour.is_refundable,
            'avg_rating': avg_rating,
            'review_count': review_count,
        })