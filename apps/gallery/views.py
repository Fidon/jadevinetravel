from django.views import View
from django.shortcuts import render

from apps.gallery.models import GalleryCategory, GalleryItem


class GalleryView(View):
    template_name = 'gallery/gallery.html'

    def get(self, request):
        categories = GalleryCategory.objects.all().order_by('order')
        lang = request.LANGUAGE_CODE or 'en'

        # Build category data with language-resolved names and item counts
        cat_data = []
        for cat in categories:
            name = (
                getattr(cat, f'name_{lang}', None)
                or cat.name_en
            )
            cat_data.append({
                'pk':        cat.pk,
                'name':      name,
                'slug':      cat.slug,
                'count':     cat.items.count(),
                # 'count':     cat.galleryitem_set.filter(
                #                  media_type='photo'
                #              ).count() +
                #              cat.galleryitem_set.filter(
                #                  media_type='video'
                #              ).count(),
            })

        # Default: show all items; filter by category if requested
        selected_slug = request.GET.get('category', '').strip()
        selected_cat  = None
        items         = GalleryItem.objects.select_related('category').order_by(
                            'category__order', 'order'
                        )

        if selected_slug:
            selected_cat = categories.filter(slug=selected_slug).first()
            if selected_cat:
                items = items.filter(category=selected_cat)

        # Resolve captions per language
        resolved_items = []
        for item in items:
            caption = (
                getattr(item, f'caption_{lang}', None)
                or item.caption_en
                or ''
            )
            resolved_items.append({
                'pk':         item.pk,
                'media_type': item.media_type,
                'image_url':  item.image.url if item.image else '',
                'video_url':  item.video_url or '',
                'caption':    caption,
                'is_featured': item.is_featured,
                'category_name': (
                    getattr(item.category, f'name_{lang}', None)
                    or item.category.name_en
                ),
            })

        context = {
            'categories':    cat_data,
            'items':         resolved_items,
            'selected_slug': selected_slug,
            'selected_cat':  selected_cat,
            'total_count':   len(resolved_items),
            'photo_count':   sum(
                1 for i in resolved_items if i['media_type'] == 'photo'
            ),
            'video_count':   sum(
                1 for i in resolved_items if i['media_type'] == 'video'
            ),
        }
        return render(request, self.template_name, context)