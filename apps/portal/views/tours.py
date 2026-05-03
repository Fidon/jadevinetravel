import json
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder

from apps.tours.models import TourPackage, TourItineraryDay, TourPhoto
from apps.portal.mixins import SuperAdminRequiredMixin
from apps.portal.forms import TourPackageForm, TourItineraryDayForm


# ===========================================================================
# TOUR LIST
# ===========================================================================

class PortalTourListView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_tours_list.html'

    def get(self, request):
        qs = TourPackage.objects.prefetch_related('photos')

        tour_type_filter = request.GET.get('tour_type', '').strip()
        search_query     = request.GET.get('q', '').strip()

        if tour_type_filter:
            qs = qs.filter(tour_type=tour_type_filter)
        if search_query:
            qs = qs.filter(name_en__icontains=search_query)

        context = {
            'tours': qs.order_by('-created_at'),
            'tour_type_filter': tour_type_filter,
            'search_query': search_query,
            'tour_type_choices': TourPackage.TOUR_TYPE_CHOICES,
        }
        return render(request, self.template_name, context)


# ===========================================================================
# TOUR DETAIL
# ===========================================================================

class PortalTourDetailView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_tour_detail.html'

    def get(self, request, pk):
        tour = get_object_or_404(
            TourPackage.objects.prefetch_related('itinerary_days', 'photos'),
            pk=pk
        )
        itinerary_days = tour.itinerary_days.order_by('day_number')
        photos = tour.photos.order_by('order')

        # Serialize itinerary days for JS modal population — same pattern as room types
        days_data = []
        for day in itinerary_days:
            days_data.append({
                'id':             day.pk,
                'day_number':     day.day_number,
                'title_en':       day.title_en or '',
                'title_fr':       day.title_fr or '',
                'title_ru':       day.title_ru or '',
                'description_en': day.description_en or '',
                'description_fr': day.description_fr or '',
                'description_ru': day.description_ru or '',
                'edit_url':  f'/portal/tours/{pk}/itinerary/{day.pk}/edit/',
                'delete_url': f'/portal/tours/{pk}/itinerary/{day.pk}/delete/',
            })

        context = {
            'tour': tour,
            'itinerary_days': itinerary_days,
            'photos': photos,
            'day_form': TourItineraryDayForm(),
            'itinerary_days_json': json.dumps(days_data, cls=DjangoJSONEncoder),
        }
        return render(request, self.template_name, context)


# ===========================================================================
# TOUR CREATE
# ===========================================================================

class PortalTourCreateView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_tour_form.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form': TourPackageForm(),
            'is_edit': False,
        })

    def post(self, request):
        form = TourPackageForm(request.POST, request.FILES)
        if form.is_valid():
            tour = form.save()
            messages.success(request, _('Tour package created successfully.'))
            return redirect('portal:tour_detail', pk=tour.pk)

        return render(request, self.template_name, {
            'form': form,
            'is_edit': False,
        })


# ===========================================================================
# TOUR EDIT
# ===========================================================================

class PortalTourEditView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_tour_form.html'

    def get(self, request, pk):
        tour = get_object_or_404(TourPackage, pk=pk)
        return render(request, self.template_name, {
            'form': TourPackageForm(instance=tour),
            'tour': tour,
            'is_edit': True,
        })

    def post(self, request, pk):
        tour = get_object_or_404(TourPackage, pk=pk)
        form = TourPackageForm(request.POST, request.FILES, instance=tour)

        if form.is_valid():
            form.save()
            messages.success(request, _('Tour package updated successfully.'))
            return redirect('portal:tour_detail', pk=tour.pk)

        return render(request, self.template_name, {
            'form': form,
            'tour': tour,
            'is_edit': True,
        })


# ===========================================================================
# TOUR DELETE
# ===========================================================================

class PortalTourDeleteView(SuperAdminRequiredMixin, View):

    def get(self, request, pk):
        return redirect('portal:tour_detail', pk=pk)

    def post(self, request, pk):
        tour = get_object_or_404(TourPackage, pk=pk)
        tour_name = tour.name_en
        tour.delete()
        messages.success(request, _(f'Tour package "{tour_name}" has been deleted.'))
        return redirect('portal:tour_list')


# ===========================================================================
# TOGGLE FEATURED
# ===========================================================================

class PortalTourToggleFeaturedView(SuperAdminRequiredMixin, View):

    def post(self, request, pk):
        tour = get_object_or_404(TourPackage, pk=pk)
        tour.is_featured = not tour.is_featured
        tour.save(update_fields=['is_featured'])
        state = _('featured') if tour.is_featured else _('unfeatured')
        messages.success(request, _(f'"{tour.name_en}" is now {state}.'))
        return redirect('portal:tour_detail', pk=pk)


# ===========================================================================
# ITINERARY DAY MANAGEMENT — modal POST
# ===========================================================================

class PortalTourDayAddView(SuperAdminRequiredMixin, View):

    def post(self, request, tpk):
        tour = get_object_or_404(TourPackage, pk=tpk)
        form = TourItineraryDayForm(request.POST)

        if form.is_valid():
            day = form.save(commit=False)
            day.package = tour
            # Enforce unique day_number per package — reject duplicate
            if tour.itinerary_days.filter(day_number=day.day_number).exists():
                messages.error(
                    request,
                    _(f'Day {day.day_number} already exists for this package. '
                      f'Edit the existing day or choose a different number.')
                )
                return redirect('portal:tour_detail', pk=tpk)
            day.save()
            messages.success(request, _(f'Day {day.day_number} added.'))
        else:
            errors = '; '.join(
                f'{f}: {", ".join(errs)}' for f, errs in form.errors.items()
            )
            messages.error(request, f'{_("Could not add day")}: {errors}')

        return redirect('portal:tour_detail', pk=tpk)


class PortalTourDayEditView(SuperAdminRequiredMixin, View):

    def post(self, request, tpk, pk):
        tour = get_object_or_404(TourPackage, pk=tpk)
        day  = get_object_or_404(TourItineraryDay, pk=pk, package=tour)
        form = TourItineraryDayForm(request.POST, instance=day)

        if form.is_valid():
            new_day_number = form.cleaned_data['day_number']
            # Allow same day_number (editing in place), block conflict with other days
            if (tour.itinerary_days
                    .filter(day_number=new_day_number)
                    .exclude(pk=day.pk)
                    .exists()):
                messages.error(
                    request,
                    _(f'Day {new_day_number} already exists. '
                      f'Choose a different day number.')
                )
                return redirect('portal:tour_detail', pk=tpk)
            form.save()
            messages.success(request, _(f'Day {new_day_number} updated.'))
        else:
            errors = '; '.join(
                f'{f}: {", ".join(errs)}' for f, errs in form.errors.items()
            )
            messages.error(request, f'{_("Could not update day")}: {errors}')

        return redirect('portal:tour_detail', pk=tpk)


class PortalTourDayDeleteView(SuperAdminRequiredMixin, View):

    def post(self, request, tpk, pk):
        tour = get_object_or_404(TourPackage, pk=tpk)
        day  = get_object_or_404(TourItineraryDay, pk=pk, package=tour)
        day_number = day.day_number
        day.delete()
        messages.success(request, _(f'Day {day_number} deleted.'))
        return redirect('portal:tour_detail', pk=tpk)


# ===========================================================================
# PHOTO MANAGEMENT — AJAX, same contract as hotels and cars
# ===========================================================================

class PortalTourPhotoUploadView(SuperAdminRequiredMixin, View):

    def post(self, request, tpk):
        tour = get_object_or_404(TourPackage, pk=tpk)
        image = request.FILES.get('image')

        if not image:
            return JsonResponse({'success': False, 'error': str(_('No image provided.'))}, status=400)

        allowed = ('image/jpeg', 'image/png', 'image/webp')
        if image.content_type not in allowed:
            return JsonResponse({'success': False, 'error': str(_('Only JPEG, PNG, and WebP images are accepted.'))}, status=400)

        if image.size > 8 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': str(_('Image must be under 8 MB.'))}, status=400)

        next_order = (
            tour.photos.order_by('-order').values_list('order', flat=True).first() or 0
        ) + 1

        photo = TourPhoto.objects.create(
            package=tour,
            image=image,
            caption=request.POST.get('caption', '').strip() or None,
            order=next_order,
        )

        return JsonResponse({
            'success': True,
            'photo_id': photo.pk,
            'url': photo.image.url,
        })


class PortalTourPhotoDeleteView(SuperAdminRequiredMixin, View):

    def post(self, request, tpk, pk):
        tour = get_object_or_404(TourPackage, pk=tpk)
        photo = get_object_or_404(TourPhoto, pk=pk, package=tour)
        photo.image.delete(save=False)
        photo.delete()
        return JsonResponse({'success': True})


class PortalTourPhotoReorderView(SuperAdminRequiredMixin, View):

    def post(self, request, tpk):
        tour = get_object_or_404(TourPackage, pk=tpk)

        try:
            data = json.loads(request.body)
            order_list = data.get('order', [])
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)

        valid_ids = set(tour.photos.values_list('id', flat=True))
        for idx, photo_id in enumerate(order_list):
            if photo_id not in valid_ids:
                return JsonResponse({'success': False, 'error': 'Invalid photo ID.'}, status=400)
            TourPhoto.objects.filter(pk=photo_id).update(order=idx)

        return JsonResponse({'success': True})