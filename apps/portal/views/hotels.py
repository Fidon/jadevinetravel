import json
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task
from django.core.serializers.json import DjangoJSONEncoder

from apps.hotels.models import Hotel, HotelPhoto, HotelRoomType, HotelRoomTypePhoto
from apps.portal.mixins import (
    PortalRequiredMixin,
    SuperAdminRequiredMixin,
    get_accessible_hotels,
    is_mini_admin,
)
from apps.portal.forms import HotelForm, HotelRoomTypeForm, HotelRejectionForm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_portal_hotel(user, pk):
    qs = get_accessible_hotels(user)
    return get_object_or_404(qs, pk=pk)


def _set_approval_on_create(hotel, user):
    if is_mini_admin(user):
        hotel.created_by = user
        hotel.approval_status = 'pending'
        hotel.is_active = False
    else:
        hotel.approval_status = 'approved'
        hotel.is_active = True


def _reset_approval_on_edit(hotel, user):
    if is_mini_admin(user) and hotel.approval_status == 'approved':
        hotel.approval_status = 'pending'
        hotel.is_active = False
        return True
    return False


# ===========================================================================
# HOTEL LIST
# ===========================================================================

class PortalHotelListView(PortalRequiredMixin, View):
    template_name = 'portal/portal_hotels_list.html'

    def get(self, request):
        qs = get_accessible_hotels(request.user).prefetch_related('photos')

        status_filter = request.GET.get('status', '').strip()
        location_filter = request.GET.get('location', '').strip()
        search_query = request.GET.get('q', '').strip()

        if status_filter:
            qs = qs.filter(approval_status=status_filter)
        if location_filter:
            qs = qs.filter(location=location_filter)
        if search_query:
            qs = qs.filter(name__icontains=search_query)

        pending_count = get_accessible_hotels(request.user).filter(
            approval_status='pending'
        ).count()

        context = {
            'hotels': qs.order_by('-created_at'),
            'status_filter': status_filter,
            'location_filter': location_filter,
            'search_query': search_query,
            'pending_count': pending_count,
            'mini_admin': is_mini_admin(request.user),
            'location_choices': Hotel.LOCATION_CHOICES,
        }
        return render(request, self.template_name, context)


# ===========================================================================
# PENDING APPROVALS QUEUE — Super Admin only
# ===========================================================================

class PortalPendingHotelsView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_hotels_list.html'

    def get(self, request):
        qs = Hotel.objects.filter(
            approval_status='pending'
        ).select_related('created_by').prefetch_related('photos').order_by('created_at')

        context = {
            'hotels': qs,
            'pending_only': True,
            'pending_count': qs.count(),
            'mini_admin': False,
        }
        return render(request, self.template_name, context)


# ===========================================================================
# HOTEL DETAIL
# ===========================================================================

class PortalHotelDetailView(PortalRequiredMixin, View):
    template_name = 'portal/portal_hotel_detail.html'

    def get(self, request, pk):
        hotel = _get_portal_hotel(request.user, pk)
        room_types = hotel.room_types.prefetch_related('room_photos').order_by('price_per_night')
        photos = hotel.photos.all().order_by('order')
        rejection_form = HotelRejectionForm()
        room_types_data = []

        for rt in room_types:
            # Serialize room type photos for JS
            rt_photos = [
                {
                    'id': p.pk,
                    'url': p.image.url,
                    'caption': p.caption or '',
                }
                for p in rt.room_photos.all()
            ]
            room_types_data.append({
                'id': rt.pk,
                'name': rt.name,
                'description_en': rt.description_en or '',
                'description_fr': rt.description_fr or '',
                'description_ru': rt.description_ru or '',
                'price_per_night': str(rt.price_per_night) if rt.price_per_night else '',
                'max_guests': rt.max_guests,
                'amenities': rt.amenities,
                'discount_percent': rt.discount_percent,
                'discount_expires_at': (
                    rt.discount_expires_at.strftime('%Y-%m-%dT%H:%M')
                    if rt.discount_expires_at else ''
                ),
                'is_refundable': rt.is_refundable,
                'allows_pay_on_arrival': rt.allows_pay_on_arrival,
                'allows_pets': rt.allows_pets,
                'is_available': rt.is_available,
                'edit_url': f'/portal/hotels/{pk}/rooms/{rt.pk}/edit/',
                'photos': rt_photos,
            })

        context = {
            'hotel': hotel,
            'room_types': room_types,
            'room_types_json': json.dumps(room_types_data, cls=DjangoJSONEncoder),
            'photos': photos,
            'rejection_form': rejection_form,
            'mini_admin': is_mini_admin(request.user),
            'room_form': HotelRoomTypeForm(),
        }
        return render(request, self.template_name, context)


# ===========================================================================
# HOTEL CREATE
# ===========================================================================

class PortalHotelCreateView(PortalRequiredMixin, View):
    template_name = 'portal/portal_hotel_form.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form': HotelForm(),
            'is_edit': False,
            'mini_admin': is_mini_admin(request.user),
        })

    def post(self, request):
        form = HotelForm(request.POST)
        if form.is_valid():
            hotel = form.save(commit=False)
            _set_approval_on_create(hotel, request.user)
            hotel.save()

            if is_mini_admin(request.user):
                async_task('apps.portal.tasks.notify_superadmin_new_listing', 'hotel', hotel.pk)
                messages.success(
                    request,
                    _('Hotel submitted for review. You will be notified once approved.')
                )
            else:
                messages.success(request, _('Hotel created and published successfully.'))

            return redirect('portal:hotel_detail', pk=hotel.pk)

        return render(request, self.template_name, {
            'form': form,
            'is_edit': False,
            'mini_admin': is_mini_admin(request.user),
        })


# ===========================================================================
# HOTEL EDIT
# ===========================================================================

class PortalHotelEditView(PortalRequiredMixin, View):
    template_name = 'portal/portal_hotel_form.html'

    def get(self, request, pk):
        hotel = _get_portal_hotel(request.user, pk)
        return render(request, self.template_name, {
            'form': HotelForm(instance=hotel),
            'hotel': hotel,
            'is_edit': True,
            'mini_admin': is_mini_admin(request.user),
            'show_approval_warning': (
                is_mini_admin(request.user) and hotel.approval_status == 'approved'
            ),
        })

    def post(self, request, pk):
        hotel = _get_portal_hotel(request.user, pk)
        form = HotelForm(request.POST, instance=hotel)

        if form.is_valid():
            hotel = form.save(commit=False)
            was_reset = _reset_approval_on_edit(hotel, request.user)
            hotel.save()

            if was_reset:
                async_task('apps.portal.tasks.notify_superadmin_new_listing', 'hotel', hotel.pk)
                messages.warning(
                    request,
                    _('Your changes have been saved. This listing has been '
                      'removed from the public site and is pending re-approval.')
                )
            else:
                messages.success(request, _('Hotel updated successfully.'))
                if (
                    not is_mini_admin(request.user)
                    and hotel.created_by
                    and hasattr(hotel.created_by, 'miniadminprofile')
                ):
                    async_task(
                        'apps.portal.tasks.send_listing_edited_by_admin_email',
                        'hotel', hotel.pk, request.user.pk,
                    )

            return redirect('portal:hotel_detail', pk=hotel.pk)

        return render(request, self.template_name, {
            'form': form,
            'hotel': hotel,
            'is_edit': True,
            'mini_admin': is_mini_admin(request.user),
            'show_approval_warning': (
                is_mini_admin(request.user) and hotel.approval_status == 'approved'
            ),
        })


# ===========================================================================
# HOTEL DELETE — Super Admin only
# ===========================================================================

class PortalHotelDeleteView(SuperAdminRequiredMixin, View):

    def get(self, request, pk):
        return redirect('portal:hotel_detail', pk=pk)

    def post(self, request, pk):
        hotel = get_object_or_404(Hotel, pk=pk)
        hotel_name = hotel.name
        hotel.delete()
        messages.success(request, _(f'Hotel "{hotel_name}" has been deleted.'))
        return redirect('portal:hotel_list')


# ===========================================================================
# APPROVE — Super Admin only
# ===========================================================================

class PortalHotelApproveView(SuperAdminRequiredMixin, View):

    def post(self, request, pk):
        hotel = get_object_or_404(Hotel, pk=pk)

        if hotel.approval_status == 'approved':
            messages.info(request, _('This hotel is already approved.'))
            return redirect('portal:hotel_detail', pk=pk)

        hotel.approval_status = 'approved'
        hotel.is_active = True
        hotel.rejection_reason = ''
        hotel.save(update_fields=['approval_status', 'is_active', 'rejection_reason'])

        if hotel.created_by and hasattr(hotel.created_by, 'miniadminprofile'):
            async_task('apps.portal.tasks.send_listing_approved_email', 'hotel', hotel.pk)

        messages.success(
            request,
            _(f'"{hotel.name}" has been approved and is now live on the public site.')
        )
        next_url = request.POST.get('next', '')
        if next_url == 'pending':
            return redirect('portal:pending_hotels')
        return redirect('portal:hotel_detail', pk=pk)


# ===========================================================================
# REJECT — Super Admin only
# ===========================================================================

class PortalHotelRejectView(SuperAdminRequiredMixin, View):

    def post(self, request, pk):
        hotel = get_object_or_404(Hotel, pk=pk)
        form = HotelRejectionForm(request.POST)

        if not form.is_valid():
            error_msg = ' '.join(
                str(e) for errors in form.errors.values() for e in errors
            )
            messages.error(request, f'{_("Rejection failed")}: {error_msg}')
            return redirect('portal:hotel_detail', pk=pk)

        hotel.approval_status = 'rejected'
        hotel.is_active = False
        hotel.rejection_reason = form.cleaned_data['rejection_reason']
        hotel.save(update_fields=['approval_status', 'is_active', 'rejection_reason'])

        if hotel.created_by and hasattr(hotel.created_by, 'miniadminprofile'):
            async_task('apps.portal.tasks.send_listing_rejected_email', 'hotel', hotel.pk)

        messages.success(
            request,
            _(f'"{hotel.name}" has been rejected. The partner has been notified.')
        )
        next_url = request.POST.get('next', '')
        if next_url == 'pending':
            return redirect('portal:pending_hotels')
        return redirect('portal:hotel_detail', pk=pk)


# ===========================================================================
# RESUBMIT — Mini-Admin only
# ===========================================================================

class PortalHotelResubmitView(PortalRequiredMixin, View):

    def post(self, request, pk):
        hotel = _get_portal_hotel(request.user, pk)

        if hotel.approval_status != 'rejected':
            messages.error(request, _('Only rejected listings can be resubmitted.'))
            return redirect('portal:hotel_detail', pk=pk)

        hotel.approval_status = 'pending'
        hotel.rejection_reason = ''
        hotel.is_active = False
        hotel.save(update_fields=['approval_status', 'rejection_reason', 'is_active'])

        async_task('apps.portal.tasks.notify_superadmin_new_listing', 'hotel', hotel.pk)
        messages.success(request, _('Your listing has been resubmitted for review.'))
        return redirect('portal:hotel_detail', pk=pk)


# ===========================================================================
# HOTEL PHOTO MANAGEMENT — AJAX
# ===========================================================================

class PortalHotelPhotoUploadView(PortalRequiredMixin, View):

    def post(self, request, hpk):
        hotel = _get_portal_hotel(request.user, hpk)
        image = request.FILES.get('image')

        if not image:
            return JsonResponse({'success': False, 'error': _('No image provided.')}, status=400)

        allowed = ('image/jpeg', 'image/png', 'image/webp')
        if image.content_type not in allowed:
            return JsonResponse(
                {'success': False, 'error': _('Only JPEG, PNG, and WebP images are accepted.')},
                status=400
            )

        if image.size > 8 * 1024 * 1024:
            return JsonResponse(
                {'success': False, 'error': _('Image must be under 8 MB.')},
                status=400
            )

        is_first = not hotel.photos.exists()
        next_order = (
            hotel.photos.order_by('-order').values_list('order', flat=True).first() or 0
        ) + 1

        photo = HotelPhoto.objects.create(
            hotel=hotel,
            image=image,
            caption=request.POST.get('caption', '').strip() or None,
            is_cover=is_first,
            order=next_order,
        )

        return JsonResponse({
            'success': True,
            'photo_id': photo.pk,
            'url': photo.image.url,
            'is_cover': photo.is_cover,
            'caption': photo.caption or '',
        })


class PortalHotelPhotoDeleteView(PortalRequiredMixin, View):

    def post(self, request, hpk, pk):
        hotel = _get_portal_hotel(request.user, hpk)
        photo = get_object_or_404(HotelPhoto, pk=pk, hotel=hotel)
        was_cover = photo.is_cover
        photo.image.delete(save=False)
        photo.delete()

        if was_cover:
            next_photo = hotel.photos.order_by('order').first()
            if next_photo:
                next_photo.is_cover = True
                next_photo.save(update_fields=['is_cover'])

        return JsonResponse({'success': True})


class PortalHotelPhotoSetCoverView(PortalRequiredMixin, View):

    def post(self, request, hpk, pk):
        hotel = _get_portal_hotel(request.user, hpk)
        photo = get_object_or_404(HotelPhoto, pk=pk, hotel=hotel)
        hotel.photos.update(is_cover=False)
        photo.is_cover = True
        photo.save(update_fields=['is_cover'])
        return JsonResponse({'success': True, 'photo_id': photo.pk})


class PortalHotelPhotoReorderView(PortalRequiredMixin, View):

    def post(self, request, hpk):
        hotel = _get_portal_hotel(request.user, hpk)

        try:
            data = json.loads(request.body)
            order_list = data.get('order', [])
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)

        if not isinstance(order_list, list):
            return JsonResponse({'success': False, 'error': 'Expected a list.'}, status=400)

        valid_ids = set(hotel.photos.values_list('id', flat=True))
        for idx, photo_id in enumerate(order_list):
            if photo_id not in valid_ids:
                return JsonResponse({'success': False, 'error': 'Invalid photo ID.'}, status=400)
            HotelPhoto.objects.filter(pk=photo_id).update(order=idx)

        return JsonResponse({'success': True})


# ===========================================================================
# ROOM TYPE PHOTO MANAGEMENT — AJAX
# Same pattern as hotel photos but scoped to HotelRoomType.
# No is_cover concept — cover is first photo by order.
# ===========================================================================

class PortalRoomTypePhotoUploadView(PortalRequiredMixin, View):

    def post(self, request, hpk, rpk):
        hotel = _get_portal_hotel(request.user, hpk)
        room_type = get_object_or_404(HotelRoomType, pk=rpk, hotel=hotel)
        image = request.FILES.get('image')

        if not image:
            return JsonResponse({'success': False, 'error': _('No image provided.')}, status=400)

        allowed = ('image/jpeg', 'image/png', 'image/webp')
        if image.content_type not in allowed:
            return JsonResponse(
                {'success': False, 'error': _('Only JPEG, PNG, and WebP images are accepted.')},
                status=400
            )

        if image.size > 8 * 1024 * 1024:
            return JsonResponse(
                {'success': False, 'error': _('Image must be under 8 MB.')},
                status=400
            )

        next_order = (
            room_type.room_photos.order_by('-order').values_list('order', flat=True).first() or 0
        ) + 1

        photo = HotelRoomTypePhoto.objects.create(
            room_type=room_type,
            image=image,
            caption=request.POST.get('caption', '').strip() or None,
            order=next_order,
        )

        return JsonResponse({
            'success': True,
            'photo_id': photo.pk,
            'url': photo.image.url,
            'caption': photo.caption or '',
        })


class PortalRoomTypePhotoDeleteView(PortalRequiredMixin, View):

    def post(self, request, hpk, rpk, pk):
        hotel = _get_portal_hotel(request.user, hpk)
        room_type = get_object_or_404(HotelRoomType, pk=rpk, hotel=hotel)
        photo = get_object_or_404(HotelRoomTypePhoto, pk=pk, room_type=room_type)
        photo.image.delete(save=False)
        photo.delete()
        return JsonResponse({'success': True})


class PortalRoomTypePhotoReorderView(PortalRequiredMixin, View):

    def post(self, request, hpk, rpk):
        hotel = _get_portal_hotel(request.user, hpk)
        room_type = get_object_or_404(HotelRoomType, pk=rpk, hotel=hotel)

        try:
            data = json.loads(request.body)
            order_list = data.get('order', [])
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)

        if not isinstance(order_list, list):
            return JsonResponse({'success': False, 'error': 'Expected a list.'}, status=400)

        valid_ids = set(room_type.room_photos.values_list('id', flat=True))
        for idx, photo_id in enumerate(order_list):
            if photo_id not in valid_ids:
                return JsonResponse({'success': False, 'error': 'Invalid photo ID.'}, status=400)
            HotelRoomTypePhoto.objects.filter(pk=photo_id).update(order=idx)

        return JsonResponse({'success': True})


# ===========================================================================
# ROOM TYPE MANAGEMENT — Modal POST endpoints
# ===========================================================================

class PortalHotelRoomAddView(PortalRequiredMixin, View):

    def post(self, request, hpk):
        hotel = _get_portal_hotel(request.user, hpk)
        form = HotelRoomTypeForm(request.POST)

        if form.is_valid():
            room = form.save(commit=False)
            room.hotel = hotel
            room.save()
            messages.success(request, _(f'Room type "{room.name}" added.'))
        else:
            errors = '; '.join(
                f'{field}: {", ".join(errs)}'
                for field, errs in form.errors.items()
            )
            messages.error(request, f'{_("Could not add room type")}: {errors}')

        return redirect('portal:hotel_detail', pk=hpk)


class PortalHotelRoomEditView(PortalRequiredMixin, View):

    def post(self, request, hpk, pk):
        hotel = _get_portal_hotel(request.user, hpk)
        room = get_object_or_404(HotelRoomType, pk=pk, hotel=hotel)
        form = HotelRoomTypeForm(request.POST, instance=room)

        if form.is_valid():
            form.save()
            messages.success(request, _(f'Room type "{room.name}" updated.'))
        else:
            errors = '; '.join(
                f'{field}: {", ".join(errs)}'
                for field, errs in form.errors.items()
            )
            messages.error(request, f'{_("Could not update room type")}: {errors}')

        return redirect('portal:hotel_detail', pk=hpk)


class PortalHotelRoomDeleteView(PortalRequiredMixin, View):

    def post(self, request, hpk, pk):
        hotel = _get_portal_hotel(request.user, hpk)
        room = get_object_or_404(HotelRoomType, pk=pk, hotel=hotel)
        room_name = room.name
        room.delete()
        messages.success(request, _(f'Room type "{room_name}" deleted.'))
        return redirect('portal:hotel_detail', pk=hpk)