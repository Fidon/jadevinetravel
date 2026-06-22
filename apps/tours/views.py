import json
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.templatetags.static import static
from django.utils.translation import gettext

from .models import TourPackage
from apps.core.models import SavedFavourite
from apps.core.seo import absolute_url, clean_text, jsonld_safe, breadcrumb_schema


class TourListView(View):
    template_name = 'tours/tour_list.html'

    def get(self, request, *args, **kwargs):
        lang = request.LANGUAGE_CODE
        qs = TourPackage.objects.filter(is_active=True).prefetch_related('photos')

        tour_type = request.GET.get('tour_type', '').strip()
        max_price = request.GET.get('max_price', '').strip()
        max_dur   = request.GET.get('max_duration', '').strip()
        search_q  = request.GET.get('q', '').strip()

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
        if search_q:
            qs = qs.filter(name_en__icontains=search_q)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            saved_ids = set()
            if request.user.is_authenticated:
                saved_ids = set(
                    SavedFavourite.objects.filter(
                        user=request.user,
                        tour_package__in=qs
                    ).values_list('tour_package_id', flat=True)
                )
            data = [self._serialize(t, lang, saved_ids) for t in qs]
            return JsonResponse({'tours': data, 'count': len(data)})

        all_tours = TourPackage.objects.filter(is_active=True)
        return render(request, self.template_name, {
            'tour_count': all_tours.count(),
        })

    def _serialize(self, tour, lang, saved_ids=None):
        from apps.reviews.models import Review
        from django.db.models import Avg, Count

        cover = tour.cover_image.url if tour.cover_image else None
        discounted = tour.get_discounted_price()
        has_discount = discounted is not None

        review_data = Review.objects.filter(
            tour_package=tour, status='approved'
        ).aggregate(avg=Avg('rating'), total=Count('id'))
        avg_rating = round(review_data['avg'], 1) if review_data['avg'] and review_data['total'] >= 1 else None
        review_count = review_data['total'] if review_data['total'] >= 1 else 0

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
            'url': reverse('tours:detail', kwargs={'slug': tour.slug}),
            'is_saved': tour.id in (saved_ids or set()),
            'item_type': 'tour',
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

        discounted_price = tour.get_discounted_price()
        display_price = discounted_price or tour.price_per_person

        review_data = Review.objects.filter(
            tour_package=tour, status='approved'
        ).aggregate(avg=Avg('rating'), total=Count('id'))
        avg_rating = round(review_data['avg'], 1) if review_data['avg'] and review_data['total'] >= 1 else None
        review_count = review_data['total'] if review_data['total'] >= 1 else 0

        is_saved = (
            request.user.is_authenticated and
            SavedFavourite.objects.filter(
                user=request.user, tour_package=tour
            ).exists()
        )

        tour_name = tour.get_name(lang)
        tour_description = tour.get_description(lang)

        # ----------------------------------------------------------------
        # SEO: per-listing meta + Product/Offer & BreadcrumbList JSON-LD.
        # ----------------------------------------------------------------
        canonical = absolute_url(request.path)
        gallery_urls = [absolute_url(p.image.url) for p in photos if p.image]
        if tour.cover_image:
            primary_image = absolute_url(tour.cover_image.url)
        elif gallery_urls:
            primary_image = gallery_urls[0]
        else:
            primary_image = absolute_url(static('images/logo.png'))
        schema_images = [primary_image] + [u for u in gallery_urls if u != primary_image]

        tour_schema = {
            "@type": "Product",
            "@id": canonical + "#product",
            "name": tour_name,
            "url": canonical,
            "description": clean_text(tour_description, 300),
            "image": schema_images,
            "category": str(tour.get_tour_type_display()),
            "brand": {"@type": "Brand", "name": "Jadevine Travel & Tours"},
            "offers": {
                "@type": "Offer",
                "price": f"{display_price:.2f}",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "url": canonical,
            },
        }
        if review_count:
            tour_schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": avg_rating,
                "reviewCount": review_count,
            }

        breadcrumbs = breadcrumb_schema([
            (gettext("Home"), absolute_url(reverse('core:home'))),
            (gettext("Safaris & Tours"), absolute_url(reverse('tours:list'))),
            (tour_name, canonical),
        ])

        structured_data = jsonld_safe({
            "@context": "https://schema.org",
            "@graph": [tour_schema, breadcrumbs],
        })

        return render(request, self.template_name, {
            'tour': tour,
            'tour_name': tour_name,
            'tour_description': tour_description,
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
            'allows_pets': tour.allows_pets,
            'avg_rating': avg_rating,
            'review_count': review_count,
            'is_saved': is_saved,
            'favourite_toggle_url': '/favourites/toggle/',
            # SEO
            'seo_title': f"{tour_name} — {gettext('Safari & Tour Package')} | Jadevine Travel & Tours",
            'seo_description': clean_text(tour_description, 155) or (
                gettext("Book the %(name)s package with Jadevine Travel & Tours.")
                % {"name": tour_name}
            ),
            'seo_image': primary_image,
            'seo_type': 'product',
            'structured_data': structured_data,
        })