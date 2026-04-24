import json
from django.views.generic import DetailView
from django.views import View
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404, render
from .models import CarRental
from apps.reviews.models import Review
from django.db.models import Avg, Count


def public_cars_qs():
    return CarRental.objects.filter(
        is_active=True,
        is_available=True,
        approval_status='approved'
    ).prefetch_related('photos')


class CarListView(View):
    template_name = 'cars/car_list.html'

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self._ajax_filter(request)
        return render(request, self.template_name, {
            'page_title': _('Car Rentals in Zanzibar & Tanzania'),
        })

    def _ajax_filter(self, request):
        qs = public_cars_qs()

        vehicle_type = request.GET.get('vehicle_type', '').strip()
        rental_mode = request.GET.get('rental_mode', '').strip()
        pickup_location = request.GET.get('pickup_location', '').strip()
        max_price = request.GET.get('max_price', '').strip()

        if vehicle_type:
            qs = qs.filter(vehicle_type=vehicle_type)
        if rental_mode == 'self_drive':
            qs = qs.filter(offers_self_drive=True)
        elif rental_mode == 'with_driver':
            qs = qs.filter(offers_driver=True)
        if pickup_location:
            # JSONField contains list of strings — filter using contains
            qs = qs.filter(pickup_locations__contains=pickup_location)
        if max_price:
            try:
                qs = qs.filter(price_per_day__lte=float(max_price))
            except ValueError:
                pass

        lang = request.LANGUAGE_CODE

        cars_data = []
        for car in qs:
            cover = car.cover_photo
            review_data = Review.objects.filter(
                car=car,
                status='approved'
            ).aggregate(avg=Avg('rating'), total=Count('id'))
            avg_rating = round(review_data['avg'], 1) if review_data['avg'] and review_data['total'] >= 3 else None
            review_count = review_data['total'] if review_data['total'] >= 3 else 0

            discounted = car.get_discounted_price()
            has_discount = discounted is not None

            cars_data.append({
                'id': car.id,
                'name': car.name,
                'slug': car.slug,
                'vehicle_type': car.get_vehicle_type_display(),
                'capacity': car.capacity,
                'transmission': car.get_transmission_display(),
                'fuel_type': car.get_fuel_type_display(),
                'price_per_day': str(car.price_per_day),
                'display_price': str(discounted) if has_discount else str(car.price_per_day),
                'has_discount': has_discount,
                'discount_percent': car.discount_percent if has_discount else 0,
                'offers_self_drive': car.offers_self_drive,
                'offers_driver': car.offers_driver,
                'allows_pay_on_arrival': car.allows_pay_on_arrival,
                'is_refundable': car.is_refundable,
                'description': car.get_description(lang)[:120] + '...' if car.get_description(lang) else '',
                'cover_photo': cover.image.url if cover else None,
                'avg_rating': avg_rating,
                'review_count': review_count,
                'url': request.build_absolute_uri(f"/cars/{car.slug}/"),
            })

        return JsonResponse({'cars': cars_data})


class CarDetailView(DetailView):
    template_name = 'cars/car_detail.html'
    context_object_name = 'car'

    def get_object(self):
        return get_object_or_404(
            CarRental.objects.prefetch_related('photos'),
            slug=self.kwargs['slug'],
            is_active=True,
            is_available=True,
            approval_status='approved'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car = self.object
        lang = self.request.LANGUAGE_CODE

        context['description'] = car.get_description(lang)
        context['photos'] = car.photos.all()
        context['pickup_locations'] = car.pickup_locations  # list of strings
        context['pickup_locations_json'] = json.dumps(car.pickup_locations)
        context['booking_prefill'] = self.request.session.pop('booking_prefill', None)
        
        review_data = Review.objects.filter(
            car=car,
            status='approved'
        ).aggregate(avg=Avg('rating'), total=Count('id'))
        context['avg_rating'] = round(review_data['avg'], 1) if review_data['avg'] and review_data['total'] >= 3 else None
        context['review_count'] = review_data['total'] if review_data['total'] >= 3 else 0

        discounted = car.get_discounted_price()
        context['has_discount'] = discounted is not None
        context['discount_percent'] = car.discount_percent
        context['discounted_price'] = str(discounted) if discounted else None
        context['display_price'] = str(discounted) if discounted else str(car.price_per_day)
        context['allows_pay_on_arrival'] = car.allows_pay_on_arrival
        context['is_refundable'] = car.is_refundable

        return context
    