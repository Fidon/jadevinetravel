from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from apps.tours.models import TourPackage
from apps.gallery.models import GalleryItem
from apps.core.models import SavedFavourite
from apps.hotels.models import Hotel
from apps.cars.models import CarRental
from django.shortcuts import render, get_object_or_404


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lang = self.request.LANGUAGE_CODE or 'en'

        packages = TourPackage.objects.filter(
            is_featured=True, is_active=True
        ).select_related()[:6]

        for pkg in packages:
            pkg.display_name = pkg.get_name(lang)
            pkg.display_highlights = pkg.get_highlights(lang)[:3]

        ctx['featured_packages'] = packages
        ctx['gallery_highlights'] = GalleryItem.objects.filter(
            is_featured=True
        ).select_related('category')[:9]
        return ctx


class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['team_members'] = []
        return ctx


class ManualView(TemplateView):
    template_name = 'core/manual.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


# ---------------------------------------------------------------------------
# Favourite Toggle
# ---------------------------------------------------------------------------
# POST /favourites/toggle/
# Body: item_type=hotel|tour|car  &  item_id=<int>
# Returns:
#   { "saved": true|false }          — on success
#   { "requires_login": true }       — when unauthenticated (HTTP 401)
#   { "error": "..." }               — on bad input (HTTP 400)
# ---------------------------------------------------------------------------

class FavouriteToggleView(View):
    """
    Toggles a SavedFavourite for the current user.
    Unauthenticated requests return 401 with requires_login=true so JS
    can redirect to /accounts/login/ without a full page reload.
    """

    # Allow GET to check state without side effects (used by detail pages
    # to initialise the heart button server-side is unnecessary — we pass
    # is_saved in template context. POST is the mutation.)
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'requires_login': True}, status=401)

        item_type = request.POST.get('item_type', '').strip()
        try:
            item_id = int(request.POST.get('item_id', ''))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid item_id.'}, status=400)

        if item_type == 'hotel':
            item = get_object_or_404(
                Hotel, pk=item_id, is_active=True, approval_status='approved'
            )
            lookup = {'user': request.user, 'hotel': item}

        elif item_type == 'tour':
            item = get_object_or_404(TourPackage, pk=item_id, is_active=True)
            lookup = {'user': request.user, 'tour_package': item}

        elif item_type == 'car':
            item = get_object_or_404(
                CarRental, pk=item_id,
                is_active=True, is_available=True, approval_status='approved'
            )
            lookup = {'user': request.user, 'car': item}

        else:
            return JsonResponse({'error': 'Invalid item_type.'}, status=400)

        fav = SavedFavourite.objects.filter(**lookup).first()

        if fav:
            fav.delete()
            return JsonResponse({'saved': False})
        else:
            SavedFavourite.objects.create(**lookup)
            return JsonResponse({'saved': True})