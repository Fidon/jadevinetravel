from django.views.generic import TemplateView
from apps.tours.models import TourPackage
from apps.gallery.models import GalleryItem
from django.shortcuts import render


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lang = self.request.LANGUAGE_CODE or 'en'

        packages = TourPackage.objects.filter(
            is_featured=True, is_active=True
        ).select_related()[:6]

        # Pre-compute the correct language fields for the template
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
        # Placeholder until Jadevine provides real team data.
        # I'll replace with actual team member dicts:
        # {'name': '...', 'role': '...', 'bio': '...', 'photo': '...'}
        ctx['team_members'] = []
        return ctx


class ManualView(TemplateView):
    template_name = 'core/manual.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)