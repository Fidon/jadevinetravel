import json
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder

from apps.gallery.models import GalleryCategory, GalleryItem
from apps.portal.mixins import SuperAdminRequiredMixin


class PortalGalleryView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_gallery.html'

    def get(self, request):
        categories = GalleryCategory.objects.all().order_by('order')
        selected_pk = request.GET.get('category', '')

        # Default to first category if none selected and categories exist
        selected_cat = None
        if selected_pk:
            selected_cat = get_object_or_404(GalleryCategory, pk=selected_pk)
        elif categories.exists():
            selected_cat = categories.first()

        items = []
        if selected_cat:
            items = GalleryItem.objects.filter(
                category=selected_cat
            ).order_by('order')

        # JSON for JS drag-to-reorder and featured toggle
        categories_json = json.dumps([
            {'id': c.pk, 'name': c.name_en}
            for c in categories
        ], cls=DjangoJSONEncoder)

        context = {
            'categories': categories,
            'selected_cat': selected_cat,
            'items': items,
            'categories_json': categories_json,
            'total_items': GalleryItem.objects.count(),
            'featured_count': GalleryItem.objects.filter(is_featured=True).count(),
        }
        return render(request, self.template_name, context)


class PortalGalleryUploadView(SuperAdminRequiredMixin, View):
    """
    Handles both photo uploads (multipart) and video URL submissions (POST field).
    Returns JSON. Called by JS sequentially for images, or directly for video URLs.
    """

    def post(self, request):
        category_pk = request.POST.get('category_id', '').strip()
        if not category_pk:
            return JsonResponse(
                {'success': False, 'error': _('No category selected.')},
                status=400
            )

        category = get_object_or_404(GalleryCategory, pk=category_pk)
        media_type = request.POST.get('media_type', 'photo')
        caption_en = request.POST.get('caption_en', '').strip() or None
        next_order = (
            GalleryItem.objects.filter(category=category)
            .order_by('-order')
            .values_list('order', flat=True)
            .first() or 0
        ) + 1

        if media_type == 'video':
            video_url = request.POST.get('video_url', '').strip()
            if not video_url:
                return JsonResponse(
                    {'success': False, 'error': _('No video URL provided.')},
                    status=400
                )
            item = GalleryItem.objects.create(
                category=category,
                media_type='video',
                video_url=video_url,
                caption_en=caption_en,
                is_featured=False,
                order=next_order,
            )
            return JsonResponse({
                'success': True,
                'item_id': item.pk,
                'media_type': 'video',
                'video_url': video_url,
                'caption': item.caption_en or '',
                'is_featured': item.is_featured,
                'order': item.order,
            })

        # Photo upload
        image = request.FILES.get('image')
        if not image:
            return JsonResponse(
                {'success': False, 'error': _('No image provided.')},
                status=400
            )

        allowed = ('image/jpeg', 'image/png', 'image/webp')
        if image.content_type not in allowed:
            return JsonResponse(
                {'success': False,
                 'error': _('Only JPEG, PNG, and WebP images are accepted.')},
                status=400
            )

        if image.size > 10 * 1024 * 1024:
            return JsonResponse(
                {'success': False, 'error': _('Image must be under 10 MB.')},
                status=400
            )

        item = GalleryItem.objects.create(
            category=category,
            media_type='photo',
            image=image,
            caption_en=caption_en,
            is_featured=False,
            order=next_order,
        )

        return JsonResponse({
            'success': True,
            'item_id': item.pk,
            'media_type': 'photo',
            'url': item.image.url,
            'caption': item.caption_en or '',
            'is_featured': item.is_featured,
            'order': item.order,
        })


class PortalGalleryDeleteView(SuperAdminRequiredMixin, View):

    def post(self, request, pk):
        item = get_object_or_404(GalleryItem, pk=pk)
        if item.image:
            item.image.delete(save=False)
        item.delete()
        return JsonResponse({'success': True})


class PortalGalleryToggleFeaturedView(SuperAdminRequiredMixin, View):

    def post(self, request, pk):
        item = get_object_or_404(GalleryItem, pk=pk)
        item.is_featured = not item.is_featured
        item.save(update_fields=['is_featured'])
        return JsonResponse({
            'success': True,
            'is_featured': item.is_featured,
            'item_id': item.pk,
        })


class PortalGalleryReorderView(SuperAdminRequiredMixin, View):

    def post(self, request):
        try:
            data = json.loads(request.body)
            order_list = data.get('order', [])
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse(
                {'success': False, 'error': 'Invalid JSON.'},
                status=400
            )

        if not isinstance(order_list, list):
            return JsonResponse(
                {'success': False, 'error': 'Expected a list.'},
                status=400
            )

        # Validate all IDs are real GalleryItem PKs before writing
        valid_ids = set(
            GalleryItem.objects.filter(
                pk__in=order_list
            ).values_list('id', flat=True)
        )
        for idx, item_id in enumerate(order_list):
            if item_id not in valid_ids:
                return JsonResponse(
                    {'success': False, 'error': 'Invalid item ID.'},
                    status=400
                )
            GalleryItem.objects.filter(pk=item_id).update(order=idx)

        return JsonResponse({'success': True})


class PortalGalleryCategoryAddView(SuperAdminRequiredMixin, View):

    def post(self, request):
        name_en = request.POST.get('name_en', '').strip()
        name_fr = request.POST.get('name_fr', '').strip() or None
        name_ru = request.POST.get('name_ru', '').strip() or None

        if not name_en:
            messages.error(request, _('Category name (English) is required.'))
            return redirect('portal:gallery')

        # Order: one after the last existing category
        last_order = (
            GalleryCategory.objects.order_by('-order')
            .values_list('order', flat=True)
            .first() or 0
        )

        GalleryCategory.objects.create(
            name_en=name_en,
            name_fr=name_fr,
            name_ru=name_ru,
            order=last_order + 1,
        )
        messages.success(request, _(f'Category "{name_en}" created.'))
        return redirect('portal:gallery')


class PortalGalleryCategoryEditView(SuperAdminRequiredMixin, View):

    def post(self, request, pk):
        category = get_object_or_404(GalleryCategory, pk=pk)
        name_en = request.POST.get('name_en', '').strip()
        name_fr = request.POST.get('name_fr', '').strip() or None
        name_ru = request.POST.get('name_ru', '').strip() or None

        if not name_en:
            messages.error(request, _('Category name (English) is required.'))
            return redirect('portal:gallery')

        category.name_en = name_en
        category.name_fr = name_fr
        category.name_ru = name_ru
        category.save(update_fields=['name_en', 'name_fr', 'name_ru'])

        messages.success(request, _(f'Category "{name_en}" updated.'))
        # Preserve selected category on redirect
        return redirect(reverse('portal:gallery') + f'?category={category.pk}')


class PortalGalleryCategoryDeleteView(SuperAdminRequiredMixin, View):

    def post(self, request, pk):
        category = get_object_or_404(GalleryCategory, pk=pk)
        item_count = category.items.count()

        if item_count > 0:
            messages.error(
                request,
                _(f'Cannot delete "{category.name_en}" — it contains '
                  f'{item_count} item(s). Delete all items first.')
            )
            return redirect(f'portal:gallery')

        cat_name = category.name_en
        category.delete()
        messages.success(request, _(f'Category "{cat_name}" deleted.'))
        return redirect('portal:gallery')