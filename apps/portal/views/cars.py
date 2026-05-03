import json
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task

from apps.cars.models import CarRental, CarPhoto
from apps.portal.mixins import (
    PortalRequiredMixin,
    SuperAdminRequiredMixin,
    get_accessible_cars,
    is_mini_admin,
)
from apps.portal.forms import CarRentalForm, CarRejectionForm


# ---------------------------------------------------------------------------
# Helpers — mirror hotel pattern exactly
# ---------------------------------------------------------------------------
def _get_portal_car(user, pk):
    qs = get_accessible_cars(user)
    return get_object_or_404(qs, pk=pk)

def _set_approval_on_create(car, user):
    if is_mini_admin(user):
        car.created_by = user
        car.approval_status = 'pending'
        car.is_active = False
    else:
        car.approval_status = 'approved'
        car.is_active = True

def _reset_approval_on_edit(car, user):
    if is_mini_admin(user) and car.approval_status == 'approved':
        car.approval_status = 'pending'
        car.is_active = False
        return True
    return False


# ===========================================================================
# CAR LIST
# ===========================================================================

class PortalCarListView(PortalRequiredMixin, View):
    template_name = 'portal/portal_cars_list.html'

    def get(self, request):
        qs = get_accessible_cars(request.user).prefetch_related('photos')

        status_filter   = request.GET.get('status', '').strip()
        type_filter     = request.GET.get('vehicle_type', '').strip()
        search_query    = request.GET.get('q', '').strip()

        if status_filter:
            qs = qs.filter(approval_status=status_filter)
        if type_filter:
            qs = qs.filter(vehicle_type=type_filter)
        if search_query:
            qs = qs.filter(name__icontains=search_query)

        pending_count = get_accessible_cars(request.user).filter(
            approval_status='pending'
        ).count()

        context = {
            'cars': qs.order_by('-created_at'),
            'status_filter': status_filter,
            'type_filter': type_filter,
            'search_query': search_query,
            'pending_count': pending_count,
            'mini_admin': is_mini_admin(request.user),
            'vehicle_type_choices': CarRental.VEHICLE_TYPE_CHOICES,
        }
        return render(request, self.template_name, context)


# ===========================================================================
# PENDING APPROVALS — Super Admin only
# ===========================================================================

class PortalPendingCarsView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_cars_list.html'

    def get(self, request):
        qs = CarRental.objects.filter(
            approval_status='pending'
        ).select_related('created_by').prefetch_related('photos').order_by('created_at')

        context = {
            'cars': qs,
            'pending_only': True,
            'pending_count': qs.count(),
            'mini_admin': False,
        }
        return render(request, self.template_name, context)


# ===========================================================================
# CAR DETAIL
# ===========================================================================

class PortalCarDetailView(PortalRequiredMixin, View):
    template_name = 'portal/portal_car_detail.html'

    def get(self, request, pk):
        car = _get_portal_car(request.user, pk)
        photos = car.photos.all().order_by('order')
        rejection_form = CarRejectionForm()

        # Serialize for JS (pickup_locations already a list)
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        car_json = json.dumps({
            'pickup_locations': car.pickup_locations or [],
        }, cls=DjangoJSONEncoder)

        context = {
            'car': car,
            'photos': photos,
            'rejection_form': rejection_form,
            'mini_admin': is_mini_admin(request.user),
            'car_json': car_json,
        }
        return render(request, self.template_name, context)


# ===========================================================================
# CAR CREATE
# ===========================================================================

class PortalCarCreateView(PortalRequiredMixin, View):
    template_name = 'portal/portal_car_form.html'

    def get(self, request):
        context = {
            'form': CarRentalForm(),
            'is_edit': False,
            'mini_admin': is_mini_admin(request.user),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = CarRentalForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)
            _set_approval_on_create(car, request.user)
            car.save()

            if is_mini_admin(request.user):
                async_task(
                    'apps.portal.tasks.notify_superadmin_new_listing',
                    'car', car.pk
                )
                messages.success(
                    request,
                    _('Car rental submitted for review. You will be notified once approved.')
                )
            else:
                messages.success(request, _('Car rental created and published successfully.'))

            return redirect('portal:car_detail', pk=car.pk)

        context = {
            'form': form,
            'is_edit': False,
            'mini_admin': is_mini_admin(request.user),
        }
        return render(request, self.template_name, context)


# ===========================================================================
# CAR EDIT
# ===========================================================================

class PortalCarEditView(PortalRequiredMixin, View):
    template_name = 'portal/portal_car_form.html'

    def get(self, request, pk):
        car = _get_portal_car(request.user, pk)
        context = {
            'form': CarRentalForm(instance=car),
            'car': car,
            'is_edit': True,
            'mini_admin': is_mini_admin(request.user),
            'show_approval_warning': (
                is_mini_admin(request.user) and car.approval_status == 'approved'
            ),
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        car = _get_portal_car(request.user, pk)
        form = CarRentalForm(request.POST, instance=car)

        if form.is_valid():
            car = form.save(commit=False)
            was_reset = _reset_approval_on_edit(car, request.user)
            car.save()

            if was_reset:
                async_task(
                    'apps.portal.tasks.notify_superadmin_new_listing',
                    'car', car.pk
                )
                messages.warning(
                    request,
                    _('Changes saved. This listing has been removed from the '
                      'public site and is pending re-approval.')
                )
            else:
                messages.success(request, _('Car rental updated successfully.'))

            return redirect('portal:car_detail', pk=car.pk)

        context = {
            'form': form,
            'car': car,
            'is_edit': True,
            'mini_admin': is_mini_admin(request.user),
            'show_approval_warning': (
                is_mini_admin(request.user) and car.approval_status == 'approved'
            ),
        }
        return render(request, self.template_name, context)


# ===========================================================================
# CAR DELETE — Super Admin only
# ===========================================================================

class PortalCarDeleteView(SuperAdminRequiredMixin, View):

    def get(self, request, pk):
        return redirect('portal:car_detail', pk=pk)

    def post(self, request, pk):
        car = get_object_or_404(CarRental, pk=pk)
        car_name = car.name
        car.delete()
        messages.success(request, _(f'"{car_name}" has been deleted.'))
        return redirect('portal:car_list')


# ===========================================================================
# APPROVE / REJECT / RESUBMIT
# ===========================================================================

class PortalCarApproveView(SuperAdminRequiredMixin, View):

    def post(self, request, pk):
        car = get_object_or_404(CarRental, pk=pk)

        if car.approval_status == 'approved':
            messages.info(request, _('This vehicle is already approved.'))
            return redirect('portal:car_detail', pk=pk)

        car.approval_status = 'approved'
        car.is_active = True
        car.rejection_reason = ''
        car.save(update_fields=['approval_status', 'is_active', 'rejection_reason'])

        if car.created_by and hasattr(car.created_by, 'miniadminprofile'):
            async_task('apps.portal.tasks.send_listing_approved_email', 'car', car.pk)

        messages.success(
            request,
            _(f'"{car.name}" has been approved and is now live.')
        )
        if request.POST.get('next') == 'pending':
            return redirect('portal:pending_cars')
        return redirect('portal:car_detail', pk=pk)


class PortalCarRejectView(SuperAdminRequiredMixin, View):

    def post(self, request, pk):
        car = get_object_or_404(CarRental, pk=pk)
        form = CarRejectionForm(request.POST)

        if not form.is_valid():
            error_msg = ' '.join(
                str(e) for errors in form.errors.values() for e in errors
            )
            messages.error(request, f'{_("Rejection failed")}: {error_msg}')
            return redirect('portal:car_detail', pk=pk)

        car.approval_status = 'rejected'
        car.is_active = False
        car.rejection_reason = form.cleaned_data['rejection_reason']
        car.save(update_fields=['approval_status', 'is_active', 'rejection_reason'])

        if car.created_by and hasattr(car.created_by, 'miniadminprofile'):
            async_task('apps.portal.tasks.send_listing_rejected_email', 'car', car.pk)

        messages.success(
            request,
            _(f'"{car.name}" has been rejected. The partner has been notified.')
        )
        if request.POST.get('next') == 'pending':
            return redirect('portal:pending_cars')
        return redirect('portal:car_detail', pk=pk)


class PortalCarResubmitView(PortalRequiredMixin, View):

    def post(self, request, pk):
        car = _get_portal_car(request.user, pk)

        if car.approval_status != 'rejected':
            messages.error(request, _('Only rejected listings can be resubmitted.'))
            return redirect('portal:car_detail', pk=pk)

        car.approval_status = 'pending'
        car.rejection_reason = ''
        car.is_active = False
        car.save(update_fields=['approval_status', 'rejection_reason', 'is_active'])

        async_task('apps.portal.tasks.notify_superadmin_new_listing', 'car', car.pk)
        messages.success(request, _('Your listing has been resubmitted for review.'))
        return redirect('portal:car_detail', pk=pk)


# ===========================================================================
# PHOTO MANAGEMENT — identical contract to hotel photos
# ===========================================================================

class PortalCarPhotoUploadView(PortalRequiredMixin, View):

    def post(self, request, cpk):
        car = _get_portal_car(request.user, cpk)
        image = request.FILES.get('image')

        if not image:
            return JsonResponse({'success': False, 'error': str(_('No image provided.'))}, status=400)

        allowed = ('image/jpeg', 'image/png', 'image/webp')
        if image.content_type not in allowed:
            return JsonResponse(
                {'success': False, 'error': str(_('Only JPEG, PNG, and WebP images are accepted.'))},
                status=400
            )

        if image.size > 8 * 1024 * 1024:
            return JsonResponse(
                {'success': False, 'error': str(_('Image must be under 8 MB.'))},
                status=400
            )

        is_first = not car.photos.exists()
        next_order = (
            car.photos.order_by('-order').values_list('order', flat=True).first() or 0
        ) + 1

        photo = CarPhoto.objects.create(
            car=car,
            image=image,
            is_cover=is_first,
            order=next_order,
        )

        return JsonResponse({
            'success': True,
            'photo_id': photo.pk,
            'url': photo.image.url,
            'is_cover': photo.is_cover,
        })


class PortalCarPhotoDeleteView(PortalRequiredMixin, View):

    def post(self, request, cpk, pk):
        car = _get_portal_car(request.user, cpk)
        photo = get_object_or_404(CarPhoto, pk=pk, car=car)
        was_cover = photo.is_cover
        photo.image.delete(save=False)
        photo.delete()

        if was_cover:
            next_photo = car.photos.order_by('order').first()
            if next_photo:
                next_photo.is_cover = True
                next_photo.save(update_fields=['is_cover'])

        return JsonResponse({'success': True})


class PortalCarPhotoSetCoverView(PortalRequiredMixin, View):

    def post(self, request, cpk, pk):
        car = _get_portal_car(request.user, cpk)
        photo = get_object_or_404(CarPhoto, pk=pk, car=car)
        car.photos.update(is_cover=False)
        photo.is_cover = True
        photo.save(update_fields=['is_cover'])
        return JsonResponse({'success': True, 'photo_id': photo.pk})


class PortalCarPhotoReorderView(PortalRequiredMixin, View):

    def post(self, request, cpk):
        car = _get_portal_car(request.user, cpk)

        try:
            data = json.loads(request.body)
            order_list = data.get('order', [])
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)

        valid_ids = set(car.photos.values_list('id', flat=True))
        for idx, photo_id in enumerate(order_list):
            if photo_id not in valid_ids:
                return JsonResponse({'success': False, 'error': 'Invalid photo ID.'}, status=400)
            CarPhoto.objects.filter(pk=photo_id).update(order=idx)

        return JsonResponse({'success': True})